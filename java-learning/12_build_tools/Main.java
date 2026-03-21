/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 12단계: 빌드 도구
  ─ Maven, Gradle, 프로젝트 구조, 의존성 관리, JAR 패키징 ─

  [학습 목표]
  1. 빌드 도구가 왜 필요한지 이해한다
  2. Maven의 pom.xml 구조를 안다
  3. Gradle의 build.gradle 구조를 안다
  4. 의존성(dependency) 관리를 이해한다
  5. 표준 프로젝트 디렉토리 구조를 안다
  6. JAR 파일 패키징을 이해한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.io.*;
import java.nio.file.*;


// =====================================================================
// 레슨 1 — 빌드 도구가 왜 필요한가?
// =====================================================================
/*
★ 빌드 도구 = 반복 작업을 자동화하는 "자동 조립 로봇"

  ┌──────────────────────────────────────────────┐
  │  비유: 빌드 도구는 "요리사의 자동 레시피"     │
  │                                              │
  │  빌드 도구 없이:                             │
  │    1. 재료 사러 가기 (의존성 직접 다운로드)  │
  │    2. 재료 손질 (컴파일)                     │
  │    3. 맛 보기 (테스트)                       │
  │    4. 포장하기 (패키징)                      │
  │    → 매번 수동으로! 실수도 잦음!             │
  │                                              │
  │  빌드 도구 사용:                             │
  │    "mvn package" 한 마디면 전부 자동!        │
  └──────────────────────────────────────────────┘

★ 빌드 도구가 하는 일
  ┌────────────────┬──────────────────────────────┐
  │ 기능           │ 설명                          │
  ├────────────────┼──────────────────────────────┤
  │ 의존성 관리    │ 필요한 라이브러리 자동 다운로드│
  │ 컴파일         │ .java → .class 변환          │
  │ 테스트         │ 단위 테스트 자동 실행          │
  │ 패키징         │ .jar, .war 파일 생성          │
  │ 배포           │ 서버에 자동 배포              │
  │ 코드 분석      │ 코드 품질 검사                │
  └────────────────┴──────────────────────────────┘

★ Maven vs Gradle
  ┌──────────────┬──────────────┬──────────────────┐
  │              │ Maven        │ Gradle           │
  ├──────────────┼──────────────┼──────────────────┤
  │ 설정 파일    │ pom.xml      │ build.gradle     │
  │ 설정 언어    │ XML          │ Groovy / Kotlin  │
  │ 빌드 속도    │ 보통         │ 빠름 (캐시)      │
  │ 유연성       │ 규칙적       │ 유연함           │
  │ 학습 곡선    │ 낮음         │ 보통             │
  │ 대표 사용처  │ Spring       │ Android, Spring  │
  └──────────────┴──────────────┴──────────────────┘
*/


// =====================================================================
// 레슨 2 — Maven 프로젝트 구조
// =====================================================================
/*
★ Maven 표준 디렉토리 구조 (Convention over Configuration)

  my-project/
  ├── pom.xml                    ← 프로젝트 설정 파일 (심장!)
  ├── src/
  │   ├── main/
  │   │   ├── java/              ← Java 소스 코드
  │   │   │   └── com/example/
  │   │   │       └── App.java
  │   │   └── resources/         ← 설정 파일, 이미지 등
  │   │       └── application.properties
  │   └── test/
  │       ├── java/              ← 테스트 코드
  │       │   └── com/example/
  │       │       └── AppTest.java
  │       └── resources/         ← 테스트용 리소스
  └── target/                    ← 빌드 결과물 (자동 생성)
      ├── classes/
      └── my-project-1.0.jar

★ 이 구조를 따르면 Maven이 "어디에 뭐가 있는지" 자동으로 앎!
  → 별도 설정 없이도 컴파일, 테스트, 패키징이 가능!
*/


// =====================================================================
// 레슨 3 — pom.xml 구조
// =====================================================================
/*
★ pom.xml = Project Object Model (프로젝트 설명서)

  ┌─────────────────────────────────────────────┐
  │  pom.xml 핵심 구성                           │
  │                                             │
  │  <project>                                  │
  │    <groupId>com.example</groupId>    ← 회사│
  │    <artifactId>my-app</artifactId>   ← 이름│
  │    <version>1.0.0</version>          ← 버전│
  │                                             │
  │    <dependencies>                           │
  │      <dependency>                           │
  │        <groupId>junit</groupId>             │
  │        <artifactId>junit</artifactId>       │
  │        <version>5.9.0</version>             │
  │      </dependency>                          │
  │    </dependencies>                          │
  │  </project>                                 │
  └─────────────────────────────────────────────┘

★ Maven 라이프사이클 (빌드 단계)
  ┌──────────────────────────────────────────┐
  │ validate → compile → test → package     │
  │         → verify → install → deploy     │
  └──────────────────────────────────────────┘

  mvn compile   → 컴파일만
  mvn test      → 컴파일 + 테스트
  mvn package   → 컴파일 + 테스트 + JAR 생성
  mvn install   → + 로컬 저장소에 설치
  mvn clean     → target/ 폴더 삭제

★ 주요 Maven 명령어
  ┌──────────────────┬───────────────────────────┐
  │ 명령어           │ 설명                       │
  ├──────────────────┼───────────────────────────┤
  │ mvn compile      │ 소스 코드 컴파일           │
  │ mvn test         │ 테스트 실행                │
  │ mvn package      │ JAR/WAR 패키징            │
  │ mvn clean        │ 빌드 결과 삭제             │
  │ mvn dependency:tree │ 의존성 트리 출력        │
  │ mvn spring-boot:run │ Spring Boot 실행        │
  └──────────────────┴───────────────────────────┘
*/


// =====================================================================
// 레슨 4 — Gradle 기초
// =====================================================================
/*
★ Gradle = Groovy/Kotlin 기반의 유연한 빌드 도구
  → Android 공식 빌드 도구이기도 함!

★ build.gradle 기본 구조 (Groovy DSL)

  plugins {
      id 'java'
      id 'application'
  }

  group = 'com.example'
  version = '1.0.0'

  repositories {
      mavenCentral()    // 라이브러리를 어디서 가져올지
  }

  dependencies {
      implementation 'com.google.guava:guava:31.1-jre'
      testImplementation 'org.junit.jupiter:junit-jupiter:5.9.0'
  }

  application {
      mainClass = 'com.example.App'
  }

★ Gradle 주요 명령어
  ┌────────────────────┬──────────────────────────┐
  │ 명령어              │ 설명                     │
  ├────────────────────┼──────────────────────────┤
  │ gradle build       │ 전체 빌드                │
  │ gradle test        │ 테스트 실행              │
  │ gradle run         │ 애플리케이션 실행        │
  │ gradle clean       │ 빌드 결과 삭제           │
  │ gradle dependencies│ 의존성 출력              │
  │ gradle tasks       │ 사용 가능한 태스크 목록  │
  └────────────────────┴──────────────────────────┘

★ Gradle Wrapper (gradlew)
  → 프로젝트에 Gradle 버전을 고정!
  → 팀원마다 다른 Gradle 버전 문제 해결
  → ./gradlew build 로 사용
*/


// =====================================================================
// 레슨 5 — 의존성 관리
// =====================================================================
/*
★ 의존성(Dependency) = 프로젝트가 사용하는 외부 라이브러리

  ┌──────────────────────────────────────────────┐
  │  비유: 의존성은 "요리 재료"                   │
  │                                              │
  │  김치찌개를 만들려면:                         │
  │    - 김치 (필수 재료 = compile 의존성)       │
  │    - 고춧가루 (선택 재료 = optional)         │
  │    - 맛 테스터 (시식용 = test 의존성)        │
  │                                              │
  │  재료를 직접 농사지을 필요 없이               │
  │  마트(Maven Central)에서 가져옴!             │
  └──────────────────────────────────────────────┘

★ 의존성 범위 (scope)
  ┌────────────────────┬──────────────────────────────┐
  │ Maven scope        │ 설명                          │
  ├────────────────────┼──────────────────────────────┤
  │ compile (기본)     │ 컴파일+실행 시 모두 필요      │
  │ provided           │ 컴파일 시만 (실행 환경 제공)  │
  │ runtime            │ 실행 시만 필요                │
  │ test               │ 테스트 시만 필요              │
  └────────────────────┴──────────────────────────────┘

★ 인기 있는 Java 라이브러리들
  ┌────────────────────┬──────────────────────────────┐
  │ 라이브러리          │ 용도                         │
  ├────────────────────┼──────────────────────────────┤
  │ Spring Boot        │ 웹 애플리케이션 프레임워크    │
  │ JUnit 5            │ 단위 테스트                  │
  │ Lombok             │ 보일러플레이트 코드 제거      │
  │ Jackson            │ JSON 처리                    │
  │ SLF4J + Logback    │ 로깅                         │
  │ Apache Commons     │ 유틸리티 모음                │
  │ Guava              │ Google 유틸리티              │
  │ Mockito            │ 테스트 모킹                  │
  └────────────────────┴──────────────────────────────┘
*/


// =====================================================================
// 레슨 6 — JAR 파일 이해
// =====================================================================
/*
★ JAR = Java ARchive (자바 압축 파일)
  → 여러 .class 파일을 하나로 묶은 ZIP 형태의 파일

  ┌──────────────────────────────────────────┐
  │  비유: JAR는 "도시락"                     │
  │                                          │
  │  .class 파일들 = 반찬                    │
  │  MANIFEST.MF = 메뉴판 (무엇이 들었는지)  │
  │  JAR 파일 = 도시락 통 (하나로 묶음!)     │
  │                                          │
  │  배달(배포)할 때 도시락 하나만 보내면 됨! │
  └──────────────────────────────────────────┘

★ JAR 만들기 (수동)
  javac Main.java                           ← 컴파일
  jar --create --file app.jar Main.class    ← JAR 생성
  java -jar app.jar                         ← JAR 실행

★ Executable JAR (실행 가능 JAR)
  MANIFEST.MF에 Main-Class를 지정해야 함:
  Main-Class: com.example.Main

★ Fat JAR (Uber JAR)
  → 모든 의존성을 하나의 JAR에 포함!
  → Spring Boot: spring-boot-maven-plugin
  → Gradle: shadow plugin
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {
    private static final Path LESSON_FOLDER = Path.of("java-learning", "12_build_tools");

    public static void main(String[] args) {
        System.out.println("■■■ Java 12단계: 빌드 도구 ■■■\n");

        // ─── 레슨 1: 빌드 도구의 필요성 ──────────────────
        System.out.println("── 레슨 1: 빌드 도구는 왜 필요한가? ─────────────");
        System.out.println("  빌드 도구 없이 수동 빌드:");
        System.out.println("    1. javac -cp lib/gson.jar:lib/junit.jar src/*.java");
        System.out.println("    2. java -cp .:lib/gson.jar Main");
        System.out.println("    3. 라이브러리 버전 업데이트? → 직접 다운로드!");
        System.out.println("    4. 팀원에게 공유? → 모든 JAR를 같이 보내야!");
        System.out.println();
        System.out.println("  빌드 도구 사용:");
        System.out.println("    1. mvn package (또는 gradle build)");
        System.out.println("    2. 끝! 의존성 자동 다운로드, 컴파일, 테스트, 패키징!");
        System.out.println();

        // ─── 레슨 2: Maven pom.xml 예제 ──────────────────
        System.out.println("── 레슨 2: Maven pom.xml 예제 ──────────────────");
        String pomXml = """
                  <?xml version="1.0" encoding="UTF-8"?>
                  <project>
                    <modelVersion>4.0.0</modelVersion>

                    <!-- ★ 프로젝트 좌표 (GAV) -->
                    <groupId>com.example</groupId>      <!-- 회사/조직 -->
                    <artifactId>my-java-app</artifactId> <!-- 프로젝트 이름 -->
                    <version>1.0.0</version>             <!-- 버전 -->

                    <properties>
                      <java.version>17</java.version>
                    </properties>

                    <!-- ★ 의존성: 필요한 라이브러리 -->
                    <dependencies>
                      <dependency>
                        <groupId>com.google.code.gson</groupId>
                        <artifactId>gson</artifactId>
                        <version>2.10.1</version>
                      </dependency>
                      <dependency>
                        <groupId>org.junit.jupiter</groupId>
                        <artifactId>junit-jupiter</artifactId>
                        <version>5.10.0</version>
                        <scope>test</scope>     <!-- 테스트 시만 사용 -->
                      </dependency>
                    </dependencies>
                  </project>
                """;
        System.out.println(pomXml);

        // ─── 레슨 3: Gradle build.gradle 예제 ────────────
        System.out.println("── 레슨 3: Gradle build.gradle 예제 ────────────");
        String buildGradle = """
                  plugins {
                      id 'java'
                      id 'application'
                  }

                  group = 'com.example'
                  version = '1.0.0'

                  java {
                      sourceCompatibility = JavaVersion.VERSION_17
                  }

                  repositories {
                      mavenCentral()    // ★ 라이브러리 저장소
                  }

                  dependencies {
                      // ★ 컴파일+실행 시 필요
                      implementation 'com.google.code.gson:gson:2.10.1'

                      // ★ 테스트 시만 필요
                      testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
                  }

                  application {
                      mainClass = 'com.example.App'
                  }

                  test {
                      useJUnitPlatform()
                  }
                """;
        System.out.println(buildGradle);

        // ─── 레슨 4: 빌드 설정 파일 시뮬레이션 ──────────
        System.out.println("── 레슨 4: 빌드 설정 파일 생성 (시뮬레이션) ────");
        try {
            Files.createDirectories(LESSON_FOLDER);

            // pom.xml 예제 파일 생성
            String pomContent = """
                    <?xml version="1.0" encoding="UTF-8"?>
                    <project xmlns="http://maven.apache.org/POM/4.0.0">
                        <modelVersion>4.0.0</modelVersion>
                        <groupId>com.study</groupId>
                        <artifactId>java-learning</artifactId>
                        <version>1.0-SNAPSHOT</version>
                        <properties>
                            <maven.compiler.source>17</maven.compiler.source>
                            <maven.compiler.target>17</maven.compiler.target>
                        </properties>
                    </project>
                    """;

            Path pomFile = LESSON_FOLDER.resolve("example-pom.xml");
            Files.writeString(pomFile, pomContent);
            System.out.println("  example-pom.xml 생성 완료: " + pomFile);

            // build.gradle 예제 파일 생성
            String gradleContent = """
                    plugins {
                        id 'java'
                    }
                    group = 'com.study'
                    version = '1.0-SNAPSHOT'
                    repositories {
                        mavenCentral()
                    }
                    dependencies {
                        testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
                    }
                    """;

            Path gradleFile = LESSON_FOLDER.resolve("example-build.gradle");
            Files.writeString(gradleFile, gradleContent);
            System.out.println("  example-build.gradle 생성 완료: " + gradleFile);

        } catch (IOException e) {
            System.out.println("  ★ 파일 생성 실패: " + e.getMessage());
        }
        System.out.println();

        // ─── 레슨 5: 빌드 명령어 정리 ──────────────────
        System.out.println("── 레슨 5: 빌드 명령어 비교 ─────────────────────");
        System.out.println("  ┌──────────────────┬────────────────┬────────────────┐");
        System.out.println("  │ 작업             │ Maven          │ Gradle         │");
        System.out.println("  ├──────────────────┼────────────────┼────────────────┤");
        System.out.println("  │ 프로젝트 생성    │ mvn archetype  │ gradle init    │");
        System.out.println("  │ 컴파일           │ mvn compile    │ gradle build   │");
        System.out.println("  │ 테스트           │ mvn test       │ gradle test    │");
        System.out.println("  │ 패키징           │ mvn package    │ gradle jar     │");
        System.out.println("  │ 실행             │ mvn exec:java  │ gradle run     │");
        System.out.println("  │ 청소             │ mvn clean      │ gradle clean   │");
        System.out.println("  │ 의존성 확인      │ mvn dep:tree   │ gradle deps    │");
        System.out.println("  └──────────────────┴────────────────┴────────────────┘");
        System.out.println();

        // ─── 레슨 6: JAR 파일 이해 ──────────────────────
        System.out.println("── 레슨 6: JAR 파일 패키징 ──────────────────────");
        System.out.println("  ★ JAR 만들기 (수동):");
        System.out.println("    javac Main.java");
        System.out.println("    jar --create --file app.jar --main-class Main Main.class");
        System.out.println("    java -jar app.jar");
        System.out.println();
        System.out.println("  ★ Fat JAR (모든 의존성 포함):");
        System.out.println("    Maven:  mvn package (spring-boot-maven-plugin)");
        System.out.println("    Gradle: gradle shadowJar (shadow plugin)");
        System.out.println();

        // MANIFEST.MF 예제
        System.out.println("  ★ MANIFEST.MF 예제:");
        System.out.println("    ┌─────────────────────────────────┐");
        System.out.println("    │ Manifest-Version: 1.0           │");
        System.out.println("    │ Main-Class: com.example.Main    │");
        System.out.println("    │ Created-By: 17.0.1 (Oracle)     │");
        System.out.println("    └─────────────────────────────────┘");
        System.out.println();

        // ─── 종합 정리 ─────────────────────────────────
        System.out.println("── 종합: 빌드 도구 선택 가이드 ──────────────────");
        System.out.println("  ┌──────────────────────────────────────────┐");
        System.out.println("  │  어떤 빌드 도구를 선택할까?              │");
        System.out.println("  ├──────────────────────────────────────────┤");
        System.out.println("  │  Spring Boot 프로젝트 → Maven or Gradle │");
        System.out.println("  │  Android 프로젝트    → Gradle (필수)    │");
        System.out.println("  │  간단한 학습 프로젝트 → Maven (쉬움)    │");
        System.out.println("  │  대규모 프로젝트     → Gradle (빠름)    │");
        System.out.println("  │  레거시 프로젝트     → 기존 것 유지     │");
        System.out.println("  └──────────────────────────────────────────┘");
        System.out.println();

        System.out.println("■■■ 12단계 학습 완료! ■■■");
    }
}
