/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 17단계: 빌드와 배포
  ─ JAR 패키징, Docker, CI/CD, 클라우드 배포, 모니터링 ─

  [학습 목표]
  1. JAR 패키징과 실행 방법을 안다
  2. Docker의 기본 개념과 Dockerfile을 이해한다
  3. CI/CD 파이프라인의 흐름을 안다
  4. 환경 변수와 설정 관리를 이해한다
  5. 클라우드 배포(AWS, GCP)의 기본 개념을 안다
  6. 모니터링과 로깅의 중요성을 안다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;


// =====================================================================
// 레슨 1 — 배포란 무엇인가?
// =====================================================================
/*
★ 배포(Deploy) = 만든 프로그램을 사용자가 쓸 수 있게 서버에 올리는 것!

  ┌──────────────────────────────────────────────────┐
  │  비유: 배포는 "음식 배달"                         │
  │                                                  │
  │  요리(개발) → 포장(빌드) → 배달(배포) → 맛봄(사용)│
  │                                                  │
  │  개발 PC에서만 돌리면? → 나만 쓸 수 있음!        │
  │  서버에 배포하면?    → 전 세계가 사용 가능!      │
  └──────────────────────────────────────────────────┘

★ 배포 과정 전체 흐름
  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
  │ 코드   │ → │ 빌드   │ → │ 테스트 │ → │ 패키징 │ → │ 배포   │
  │ 작성   │   │ compile│   │ test   │   │ JAR    │   │ deploy │
  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘
*/


// =====================================================================
// 레슨 2 — JAR 패키징과 실행
// =====================================================================
/*
★ JAR 패키징 단계

  ┌──────────────────────────────────────────────────┐
  │  1. 컴파일:  javac -d out src/*.java             │
  │  2. JAR 생성: jar --create --file app.jar        │
  │               --main-class Main -C out .         │
  │  3. 실행:    java -jar app.jar                   │
  └──────────────────────────────────────────────────┘

★ Maven으로 패키징
  mvn clean package
  → target/my-app-1.0.0.jar 생성!

★ Gradle로 패키징
  gradle build
  → build/libs/my-app-1.0.0.jar 생성!

★ Spring Boot Fat JAR
  → 모든 의존성을 하나의 JAR에 포함!
  → java -jar app.jar 한 줄로 실행 가능!
*/


// =====================================================================
// 레슨 3 — Docker 기초
// =====================================================================
/*
★ Docker = "컨테이너"라는 가벼운 가상 환경에 앱을 담는 기술

  ┌──────────────────────────────────────────────────┐
  │  비유: Docker는 "택배 컨테이너"                   │
  │                                                  │
  │  문제: "내 컴퓨터에서는 되는데 서버에서 안 돼요!" │
  │                                                  │
  │  해결: 앱 + 환경(JDK, 설정) 전부를 컨테이너에    │
  │        담아서 보내면 어디서든 똑같이 실행!         │
  └──────────────────────────────────────────────────┘

★ Docker 핵심 개념
  ┌────────────────┬──────────────────────────────────┐
  │ 개념           │ 설명                              │
  ├────────────────┼──────────────────────────────────┤
  │ Image          │ 컨테이너의 "설계도" (읽기 전용)   │
  │ Container      │ 이미지의 "실행 인스턴스"           │
  │ Dockerfile     │ 이미지를 만드는 "레시피"           │
  │ Docker Hub     │ 이미지 저장소 (앱 스토어!)         │
  │ Volume         │ 데이터 영구 저장 (컨테이너 삭제 후)│
  │ Network        │ 컨테이너 간 통신                   │
  └────────────────┴──────────────────────────────────┘

★ Dockerfile 예시 (Java 앱)
  ┌──────────────────────────────────────────────┐
  │ FROM eclipse-temurin:17-jre-alpine           │ ← 베이스 이미지
  │ WORKDIR /app                                 │ ← 작업 디렉토리
  │ COPY target/app.jar app.jar                  │ ← JAR 복사
  │ EXPOSE 8080                                  │ ← 포트 노출
  │ CMD ["java", "-jar", "app.jar"]              │ ← 실행 명령
  └──────────────────────────────────────────────┘

★ Docker 명령어
  ┌─────────────────────────┬──────────────────────────┐
  │ 명령어                   │ 설명                     │
  ├─────────────────────────┼──────────────────────────┤
  │ docker build -t app .   │ 이미지 빌드              │
  │ docker run -p 8080:8080 │ 컨테이너 실행            │
  │ docker ps               │ 실행 중 컨테이너 목록    │
  │ docker stop <id>        │ 컨테이너 중지            │
  │ docker logs <id>        │ 로그 확인                │
  │ docker-compose up       │ 여러 컨테이너 동시 실행  │
  └─────────────────────────┴──────────────────────────┘
*/


// =====================================================================
// 레슨 4 — CI/CD
// =====================================================================
/*
★ CI/CD = 코드 변경부터 배포까지 자동화!

  CI = Continuous Integration (지속적 통합)
  → 코드를 push하면 자동으로 빌드 + 테스트!

  CD = Continuous Deployment (지속적 배포)
  → 테스트 통과 후 자동으로 서버에 배포!

  ┌──────────────────────────────────────────────────────────┐
  │  비유: CI/CD는 "자동 품질 관리 공장"                      │
  │                                                          │
  │  수동 방식: 코드 작성 → 수동 빌드 → 수동 테스트 → 수동 배포│
  │  CI/CD:    코드 push → 자동 빌드 → 자동 테스트 → 자동 배포│
  └──────────────────────────────────────────────────────────┘

★ CI/CD 파이프라인
  ┌──────┐  ┌───────┐  ┌──────┐  ┌────────┐  ┌──────┐
  │ push │→ │ build │→ │ test │→ │ deploy │→ │ live │
  │ 코드 │  │ 빌드  │  │ 검증 │  │ 배포   │  │ 운영 │
  └──────┘  └───────┘  └──────┘  └────────┘  └──────┘
     ↑ 실패 시 알림! ────────────────────┘

★ 대표적인 CI/CD 도구
  ┌──────────────────┬──────────────────────────────┐
  │ 도구             │ 특징                          │
  ├──────────────────┼──────────────────────────────┤
  │ GitHub Actions   │ GitHub 내장, YAML 설정       │
  │ Jenkins          │ 가장 오래된 CI/CD, 자체 호스팅│
  │ GitLab CI        │ GitLab 내장                  │
  │ CircleCI         │ 클라우드 기반                 │
  │ AWS CodePipeline │ AWS 전용                     │
  └──────────────────┴──────────────────────────────┘

★ GitHub Actions 예시 (.github/workflows/ci.yml)
  name: Java CI
  on: [push, pull_request]
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-java@v4
          with:
            java-version: '17'
            distribution: 'temurin'
        - run: mvn clean test
        - run: mvn package
*/


// =====================================================================
// 레슨 5 — 환경 변수와 설정 관리
// =====================================================================
/*
★ 환경에 따라 설정이 달라야 함!

  ┌────────────────┬──────────────┬──────────────┐
  │                │ 개발 환경    │ 운영 환경    │
  ├────────────────┼──────────────┼──────────────┤
  │ DB 주소        │ localhost    │ db.prod.com  │
  │ DB 비밀번호    │ test1234     │ 매우 복잡    │
  │ 로그 레벨      │ DEBUG        │ WARN         │
  │ 포트           │ 8080         │ 443          │
  └────────────────┴──────────────┴──────────────┘

★ 설정 관리 방법
  1. application.properties / application.yml
  2. 환경 변수 (System.getenv)
  3. 프로파일 (application-dev.yml, application-prod.yml)
  4. 외부 설정 서버 (Spring Cloud Config)

★ 절대 하면 안 되는 것!
  → 코드에 비밀번호를 직접 쓰지 말 것! (하드코딩)
  → String password = "mySecret123";  ← 절대 안 됨!
  → String password = System.getenv("DB_PASSWORD");  ← 올바른 방법!
*/


// =====================================================================
// 레슨 6 — 클라우드와 모니터링
// =====================================================================
/*
★ 클라우드 배포 옵션
  ┌────────────────────┬──────────────────────────────┐
  │ 서비스             │ 특징                          │
  ├────────────────────┼──────────────────────────────┤
  │ AWS EC2            │ 가상 서버 (직접 관리)         │
  │ AWS ECS/EKS        │ Docker/Kubernetes 관리형     │
  │ AWS Lambda         │ 서버리스 (코드만 올림!)      │
  │ Google Cloud Run   │ 컨테이너 서버리스            │
  │ Heroku             │ 가장 간단한 배포             │
  │ Railway/Render     │ 간편한 클라우드              │
  └────────────────────┴──────────────────────────────┘

★ 모니터링 = "서버 건강 검진"
  → 배포 후에도 앱이 잘 동작하는지 감시!

  ┌────────────────────┬──────────────────────────────┐
  │ 모니터링 항목      │ 도구                          │
  ├────────────────────┼──────────────────────────────┤
  │ 로그               │ ELK Stack, Datadog          │
  │ 메트릭 (CPU, 메모리)│ Prometheus + Grafana        │
  │ 에러 추적          │ Sentry                       │
  │ APM (성능)         │ New Relic, Datadog APM      │
  │ 헬스 체크          │ Spring Actuator             │
  └────────────────────┴──────────────────────────────┘
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {
    private static final Path LESSON_FOLDER = Path.of("java-learning", "17_build_deploy");

    public static void main(String[] args) {
        System.out.println("■■■ Java 17단계: 빌드와 배포 ■■■\n");

        // ─── 레슨 1: 배포 프로세스 ──────────────────────
        System.out.println("── 레슨 1: 배포 프로세스 ────────────────────────");
        System.out.println("  전체 흐름:");
        System.out.println("  코드 작성 → 빌드 → 테스트 → 패키징 → 배포 → 운영");
        System.out.println();
        System.out.println("  각 단계에서 하는 일:");
        System.out.println("    빌드:   .java → .class (컴파일)");
        System.out.println("    테스트:  단위/통합 테스트 실행");
        System.out.println("    패키징:  .class → .jar (묶기)");
        System.out.println("    배포:   JAR → 서버 업로드 + 실행");
        System.out.println();

        // ─── 레슨 2: JAR 패키징 ─────────────────────────
        System.out.println("── 레슨 2: JAR 패키징과 실행 ────────────────────");
        System.out.println("  ★ 수동 JAR 생성:");
        System.out.println("    javac -d out Main.java");
        System.out.println("    jar --create --file app.jar --main-class Main -C out .");
        System.out.println("    java -jar app.jar");
        System.out.println();
        System.out.println("  ★ Maven JAR 생성:");
        System.out.println("    mvn clean package");
        System.out.println("    java -jar target/my-app-1.0.0.jar");
        System.out.println();
        System.out.println("  ★ Gradle JAR 생성:");
        System.out.println("    gradle build");
        System.out.println("    java -jar build/libs/my-app-1.0.0.jar");
        System.out.println();

        // ─── 레슨 3: Dockerfile 예제 생성 ────────────────
        System.out.println("── 레슨 3: Docker 파일 생성 (시뮬레이션) ────────");
        try {
            Files.createDirectories(LESSON_FOLDER);

            String dockerfile = """
                    # Java 17 기반 Docker 이미지
                    FROM eclipse-temurin:17-jre-alpine

                    # 작업 디렉토리 설정
                    WORKDIR /app

                    # JAR 파일 복사
                    COPY target/app.jar app.jar

                    # 포트 노출
                    EXPOSE 8080

                    # 실행 명령
                    CMD ["java", "-jar", "app.jar"]
                    """;

            Path dockerfilePath = LESSON_FOLDER.resolve("Dockerfile.example");
            Files.writeString(dockerfilePath, dockerfile);
            System.out.println("  Dockerfile.example 생성 완료");
            System.out.println("  내용:");
            for (String line : dockerfile.split("\n")) {
                System.out.println("    " + line);
            }

            // docker-compose.yml 예제
            String dockerCompose = """
                    version: '3.8'
                    services:
                      app:
                        build: .
                        ports:
                          - "8080:8080"
                        environment:
                          - DB_HOST=db
                          - DB_PORT=5432
                        depends_on:
                          - db
                      db:
                        image: postgres:15-alpine
                        environment:
                          - POSTGRES_DB=myapp
                          - POSTGRES_USER=user
                          - POSTGRES_PASSWORD=password
                        volumes:
                          - db_data:/var/lib/postgresql/data
                    volumes:
                      db_data:
                    """;

            Path composePath = LESSON_FOLDER.resolve("docker-compose.example.yml");
            Files.writeString(composePath, dockerCompose);
            System.out.println("  docker-compose.example.yml 생성 완료");

        } catch (IOException e) {
            System.out.println("  ★ 파일 생성 실패: " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 4: CI/CD 파이프라인 ───────────────────
        System.out.println("── 레슨 4: CI/CD 파이프라인 ─────────────────────");
        try {
            String githubAction = """
                    name: Java CI/CD Pipeline
                    on:
                      push:
                        branches: [main]
                      pull_request:
                        branches: [main]

                    jobs:
                      build-and-test:
                        runs-on: ubuntu-latest
                        steps:
                          - uses: actions/checkout@v4
                          - name: Set up JDK 17
                            uses: actions/setup-java@v4
                            with:
                              java-version: '17'
                              distribution: 'temurin'
                          - name: Build
                            run: mvn compile
                          - name: Test
                            run: mvn test
                          - name: Package
                            run: mvn package -DskipTests

                      deploy:
                        needs: build-and-test
                        runs-on: ubuntu-latest
                        if: github.ref == 'refs/heads/main'
                        steps:
                          - name: Deploy to server
                            run: echo "배포 스크립트 실행"
                    """;

            Path actionPath = LESSON_FOLDER.resolve("ci-cd-example.yml");
            Files.writeString(actionPath, githubAction);
            System.out.println("  GitHub Actions 예제 생성 완료");
            System.out.println();
            System.out.println("  CI/CD 파이프라인 단계:");
            System.out.println("    ┌──────┐  ┌───────┐  ┌──────┐  ┌────────┐");
            System.out.println("    │ push │→ │ build │→ │ test │→ │ deploy │");
            System.out.println("    └──────┘  └───────┘  └──────┘  └────────┘");
            System.out.println("      자동!    자동!       자동!     자동!");

        } catch (IOException e) {
            System.out.println("  ★ 파일 생성 실패: " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 5: 환경 변수 시뮬레이션 ───────────────
        System.out.println("── 레슨 5: 환경 변수와 설정 관리 ───────────────");

        // 환경 변수 읽기 시뮬레이션
        String javaHome = System.getenv("JAVA_HOME");
        String path = System.getenv("PATH");
        String dbHost = System.getenv("DB_HOST");  // 아마 null

        System.out.println("  JAVA_HOME: " + (javaHome != null ? javaHome : "(미설정)"));
        System.out.println("  DB_HOST:   " + (dbHost != null ? dbHost : "(미설정 → 기본값 사용)"));
        System.out.println();

        // 환경별 설정 시뮬레이션
        String env = System.getenv("APP_ENV");
        if (env == null) env = "development";

        System.out.println("  현재 환경: " + env);
        System.out.println("  ┌────────────┬─────────────────┬─────────────────┐");
        System.out.println("  │ 설정       │ development     │ production      │");
        System.out.println("  ├────────────┼─────────────────┼─────────────────┤");
        System.out.println("  │ DB Host    │ localhost       │ db.prod.com     │");
        System.out.println("  │ Log Level  │ DEBUG           │ WARN            │");
        System.out.println("  │ Port       │ 8080            │ 443             │");
        System.out.println("  └────────────┴─────────────────┴─────────────────┘");
        System.out.println();

        // ─── 레슨 6: 배포 매니페스트 ────────────────────
        System.out.println("── 레슨 6: 배포 매니페스트 생성 ────────────────");
        try {
            String timestamp = LocalDateTime.now()
                    .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

            String manifest = """
                    ==============================
                    배포 매니페스트
                    ==============================
                    앱 이름:    java-learning
                    버전:       1.0.0
                    빌드 시간:  %s
                    Java 버전:  %s
                    OS:         %s
                    ==============================
                    """.formatted(
                    timestamp,
                    System.getProperty("java.version"),
                    System.getProperty("os.name")
            );

            Path manifestPath = LESSON_FOLDER.resolve("deploy-manifest.txt");
            Files.writeString(manifestPath, manifest);
            System.out.println("  매니페스트 생성:");
            for (String line : manifest.split("\n")) {
                System.out.println("    " + line);
            }
        } catch (IOException e) {
            System.out.println("  ★ 실패: " + e.getMessage());
        }
        System.out.println();

        // ─── 종합 정리 ──────────────────────────────────
        System.out.println("── 종합: 배포 체크리스트 ────────────────────────");
        System.out.println("  ┌──────────────────────────────────────────────┐");
        System.out.println("  │  배포 전 체크리스트                          │");
        System.out.println("  ├──────────────────────────────────────────────┤");
        System.out.println("  │  □ 모든 테스트가 통과하는가?                │");
        System.out.println("  │  □ 환경 변수가 올바르게 설정되었나?          │");
        System.out.println("  │  □ 코드에 하드코딩된 비밀번호는 없나?       │");
        System.out.println("  │  □ 로그 레벨이 적절한가?                    │");
        System.out.println("  │  □ 롤백 계획이 있는가?                      │");
        System.out.println("  │  □ 모니터링이 설정되어 있는가?              │");
        System.out.println("  │  □ DB 마이그레이션이 준비되었나?            │");
        System.out.println("  │  □ 문서(README)가 최신인가?                │");
        System.out.println("  └──────────────────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 17단계 학습 완료! ■■■");
    }
}
