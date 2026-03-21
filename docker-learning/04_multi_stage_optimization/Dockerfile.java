# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: Dockerfile.java
# ■ 목적: Java 멀티스테이지 빌드 - JDK 빌드 → JRE 런타임
# ■ 비교: JDK 이미지 ~400MB → JRE 이미지 ~200MB
# ■ 빌드: docker build -f Dockerfile.java -t java-optimized .
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# ============================================================
# 스테이지 1: 의존성 캐싱
# ============================================================
# Maven/Gradle 의존성을 먼저 다운로드해서 캐싱
# pom.xml이 바뀌지 않으면 다시 다운로드하지 않아
FROM eclipse-temurin:21-jdk-alpine AS deps

WORKDIR /build

# Maven Wrapper 복사 (프로젝트에 포함된 Maven)
COPY mvnw pom.xml ./
COPY .mvn .mvn

# 의존성만 다운로드 (소스코드 컴파일은 안 해)
# -B = batch mode (대화형 입력 없이)
# dependency:go-offline = 모든 의존성을 미리 다운로드
RUN chmod +x mvnw && \
    ./mvnw dependency:go-offline -B

# ============================================================
# 스테이지 2: 빌드 (Build)
# ============================================================
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build

# deps 스테이지에서 다운로드한 의존성 복사
COPY --from=deps /root/.m2 /root/.m2

# 전체 소스코드 복사
COPY . .

# 애플리케이션 빌드
# package = 컴파일 + 테스트 + JAR 파일 생성
# -DskipTests = 테스트 건너뛰기 (CI/CD에서 별도로 하니까)
# spring-boot:repackage = 실행 가능한 fat JAR 생성
RUN chmod +x mvnw && \
    ./mvnw package -DskipTests -B

# JAR 파일에서 레이어 추출 (Spring Boot layered JAR)
# Spring Boot 2.3+부터 JAR을 레이어로 분리할 수 있어
# → Docker 캐싱 효율이 올라가 (변경된 레이어만 다시 빌드)
RUN mkdir -p /extracted && \
    java -Djarmode=layertools -jar target/*.jar extract --destination /extracted

# ============================================================
# 스테이지 3: 프로덕션 (JRE만!)
# ============================================================
# JDK = 개발 도구 포함 (컴파일러, 디버거 등) → 크고 불필요
# JRE = 실행만 가능 → 작고 충분해!
FROM eclipse-temurin:21-jre-alpine AS production

# 보안: 일반 사용자 생성
RUN addgroup -S app && adduser -S -G app app

WORKDIR /app

# Spring Boot 레이어를 순서대로 복사
# 아래부터 위로 갈수록 자주 바뀌는 것
# → 자주 바뀌지 않는 것을 먼저 복사 = 캐시 효율 극대화!
COPY --from=builder --chown=app:app /extracted/dependencies/ ./
COPY --from=builder --chown=app:app /extracted/spring-boot-loader/ ./
COPY --from=builder --chown=app:app /extracted/snapshot-dependencies/ ./
COPY --from=builder --chown=app:app /extracted/application/ ./

# 레이어 순서 설명:
# 1. dependencies = 외부 라이브러리 (거의 안 바뀜)
# 2. spring-boot-loader = 부트 로더 (거의 안 바뀜)
# 3. snapshot-dependencies = 개발 중인 라이브러리 (가끔 바뀜)
# 4. application = 우리 코드 (자주 바뀜) → 맨 마지막!

# JVM 최적화 환경변수
# 컨테이너 환경에 맞는 JVM 설정
ENV JAVA_OPTS="-XX:+UseContainerSupport \
    -XX:MaxRAMPercentage=75.0 \
    -XX:InitialRAMPercentage=50.0 \
    -Djava.security.egd=file:/dev/urandom"
# UseContainerSupport = 컨테이너의 메모리 제한을 JVM이 인식
# MaxRAMPercentage = 컨테이너 메모리의 75%까지 사용
# urandom = 빠른 난수 생성 (시작 속도 향상)

# 포트 문서화
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# 일반 사용자로 전환
USER app

# Spring Boot 실행
# JarLauncher = Spring Boot의 레이어 구조를 이해하는 런처
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
