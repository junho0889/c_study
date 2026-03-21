/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  C# 학습 17단계: 빌드와 배포
  ─ .csproj, Solution, dotnet CLI, 빌드 구성, 배포 방식 ─

  ■ 컴파일: dotnet build
  ■ 실행:   dotnet run

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  [학습 목표]
  1. .csproj 프로젝트 파일의 구조를 이해한다
  2. Solution(.sln)과 여러 프로젝트 구조를 안다
  3. dotnet CLI의 주요 명령어를 익힌다
  4. Debug vs Release 빌드 차이를 안다
  5. 다양한 배포 방식(FDD, SCD, AOT)을 이해한다
  6. 환경별 설정(appsettings, 환경변수)을 안다
  7. CI/CD의 기본 개념을 이해한다

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Lesson17
{
    class Program
    {
        private static readonly string DataFolder = Path.Combine(
            AppContext.BaseDirectory, "lesson17_data"
        );

        // =====================================================================
        // 레슨 1 — .csproj 프로젝트 파일
        // =====================================================================
        /*
        ★ .csproj = 프로젝트의 설정 파일 (XML 형식)
          → 빌드 대상, 패키지, 설정 등 모든 프로젝트 정보를 담음

        ★ 비유: 요리 재료 목록
          어떤 재료(패키지)가 필요하고,
          어떤 방법(설정)으로 요리(빌드)할지 적어둔 목록
        */
        static void Lesson1CsprojStructure()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 1: .csproj — 프로젝트 설정 파일");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ★ .csproj 기본 구조:");
            Console.WriteLine();
            Console.WriteLine("  <Project Sdk=\"Microsoft.NET.Sdk\">");
            Console.WriteLine();
            Console.WriteLine("    <PropertyGroup>");
            Console.WriteLine("      <OutputType>Exe</OutputType>");
            Console.WriteLine("      <TargetFramework>net8.0</TargetFramework>");
            Console.WriteLine("      <Nullable>enable</Nullable>");
            Console.WriteLine("      <ImplicitUsings>enable</ImplicitUsings>");
            Console.WriteLine("      <RootNamespace>MyApp</RootNamespace>");
            Console.WriteLine("    </PropertyGroup>");
            Console.WriteLine();
            Console.WriteLine("    <ItemGroup>");
            Console.WriteLine("      <PackageReference Include=\"Serilog\" Version=\"3.1.1\" />");
            Console.WriteLine("      <PackageReference Include=\"Newtonsoft.Json\" Version=\"13.0.3\" />");
            Console.WriteLine("    </ItemGroup>");
            Console.WriteLine();
            Console.WriteLine("    <ItemGroup>");
            Console.WriteLine("      <ProjectReference Include=\"../MyLib/MyLib.csproj\" />");
            Console.WriteLine("    </ItemGroup>");
            Console.WriteLine();
            Console.WriteLine("  </Project>");
            Console.WriteLine();

            Console.WriteLine("  ★ 주요 속성 설명:");
            Console.WriteLine("  ┌──────────────────────┬──────────────────────────────┐");
            Console.WriteLine("  │ 속성                 │ 설명                         │");
            Console.WriteLine("  ├──────────────────────┼──────────────────────────────┤");
            Console.WriteLine("  │ OutputType           │ Exe(실행파일) / Library(DLL) │");
            Console.WriteLine("  │ TargetFramework      │ net8.0, net9.0 등            │");
            Console.WriteLine("  │ Nullable             │ null 참조 타입 경고 활성화   │");
            Console.WriteLine("  │ ImplicitUsings       │ 기본 using 자동 추가         │");
            Console.WriteLine("  │ PackageReference     │ NuGet 패키지 참조            │");
            Console.WriteLine("  │ ProjectReference     │ 다른 프로젝트 참조           │");
            Console.WriteLine("  │ AssemblyVersion      │ 어셈블리 버전                │");
            Console.WriteLine("  └──────────────────────┴──────────────────────────────┘");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 2: Solution과 프로젝트 구조
        // ─────────────────────────────────────────────
        static void Lesson2SolutionStructure()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 2: Solution — 여러 프로젝트 관리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ Solution(.sln) = 여러 프로젝트를 하나로 묶는 파일
              → Visual Studio가 여는 최상위 파일

            ★ 전형적인 .NET 프로젝트 구조:
            */

            Console.WriteLine("  ★ 전형적인 프로젝트 구조:");
            Console.WriteLine("  MyApp.sln");
            Console.WriteLine("  ├── src/");
            Console.WriteLine("  │   ├── MyApp.Api/           ← Web API 프로젝트");
            Console.WriteLine("  │   │   ├── Controllers/");
            Console.WriteLine("  │   │   ├── Program.cs");
            Console.WriteLine("  │   │   └── MyApp.Api.csproj");
            Console.WriteLine("  │   ├── MyApp.Core/          ← 핵심 비즈니스 로직");
            Console.WriteLine("  │   │   ├── Models/");
            Console.WriteLine("  │   │   ├── Services/");
            Console.WriteLine("  │   │   └── MyApp.Core.csproj");
            Console.WriteLine("  │   └── MyApp.Data/          ← 데이터 접근 계층");
            Console.WriteLine("  │       ├── Repositories/");
            Console.WriteLine("  │       └── MyApp.Data.csproj");
            Console.WriteLine("  └── tests/");
            Console.WriteLine("      ├── MyApp.Core.Tests/    ← 단위 테스트");
            Console.WriteLine("      └── MyApp.Api.Tests/     ← 통합 테스트");
            Console.WriteLine();

            Console.WriteLine("  ★ Solution 관련 명령어:");
            Console.WriteLine("    dotnet new sln -n MyApp              솔루션 생성");
            Console.WriteLine("    dotnet sln add src/MyApp.Api         프로젝트 추가");
            Console.WriteLine("    dotnet sln list                      프로젝트 목록");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 3: dotnet CLI 명령어
        // ─────────────────────────────────────────────
        static void Lesson3DotnetCli()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 3: dotnet CLI — 핵심 명령어 모음");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────────────────────┬──────────────────────────┐");
            Console.WriteLine("  │ 명령어                          │ 설명                     │");
            Console.WriteLine("  ├──────────────────────────────────┼──────────────────────────┤");
            Console.WriteLine("  │ 프로젝트 생성                   │                          │");
            Console.WriteLine("  │ dotnet new console -n MyApp     │ 콘솔 앱 생성             │");
            Console.WriteLine("  │ dotnet new webapi -n MyApi      │ Web API 생성             │");
            Console.WriteLine("  │ dotnet new classlib -n MyLib    │ 클래스 라이브러리         │");
            Console.WriteLine("  │ dotnet new xunit -n MyTests     │ 테스트 프로젝트          │");
            Console.WriteLine("  ├──────────────────────────────────┼──────────────────────────┤");
            Console.WriteLine("  │ 빌드 & 실행                     │                          │");
            Console.WriteLine("  │ dotnet build                    │ 빌드                     │");
            Console.WriteLine("  │ dotnet run                      │ 빌드 + 실행              │");
            Console.WriteLine("  │ dotnet build -c Release         │ Release 모드 빌드        │");
            Console.WriteLine("  │ dotnet clean                    │ 빌드 결과 삭제           │");
            Console.WriteLine("  ├──────────────────────────────────┼──────────────────────────┤");
            Console.WriteLine("  │ 패키지                          │                          │");
            Console.WriteLine("  │ dotnet add package [이름]       │ NuGet 패키지 추가        │");
            Console.WriteLine("  │ dotnet remove package [이름]    │ 패키지 제거              │");
            Console.WriteLine("  │ dotnet restore                  │ 종속성 복원              │");
            Console.WriteLine("  ├──────────────────────────────────┼──────────────────────────┤");
            Console.WriteLine("  │ 테스트 & 배포                   │                          │");
            Console.WriteLine("  │ dotnet test                     │ 테스트 실행              │");
            Console.WriteLine("  │ dotnet publish -c Release       │ 배포용 빌드              │");
            Console.WriteLine("  │ dotnet publish --self-contained │ 자체 포함 배포           │");
            Console.WriteLine("  └──────────────────────────────────┴──────────────────────────┘");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 4: Debug vs Release 빌드
        // ─────────────────────────────────────────────
        static void Lesson4DebugVsRelease()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 4: Debug vs Release — 빌드 구성");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ┌──────────────────┬──────────────────┬──────────────────┐");
            Console.WriteLine("  │                  │ Debug            │ Release          │");
            Console.WriteLine("  ├──────────────────┼──────────────────┼──────────────────┤");
            Console.WriteLine("  │ 최적화           │ ✗ 없음          │ ✓ 최적화됨      │");
            Console.WriteLine("  │ 디버그 심볼      │ ✓ 포함          │ ✗ 최소          │");
            Console.WriteLine("  │ Debug.WriteLine  │ ✓ 출력됨        │ ✗ 무시됨        │");
            Console.WriteLine("  │ #if DEBUG        │ ✓ 실행됨        │ ✗ 건너뜀        │");
            Console.WriteLine("  │ 실행 속도        │ 느림             │ 빠름             │");
            Console.WriteLine("  │ 파일 크기        │ 큼               │ 작음             │");
            Console.WriteLine("  │ 용도             │ 개발 중          │ 배포/프로덕션    │");
            Console.WriteLine("  └──────────────────┴──────────────────┴──────────────────┘");
            Console.WriteLine();

#if DEBUG
            Console.WriteLine("  현재 빌드: DEBUG");
#else
            Console.WriteLine("  현재 빌드: RELEASE");
#endif
            Console.WriteLine();

            Console.WriteLine("  ★ 명령어:");
            Console.WriteLine("    dotnet build                   (기본: Debug)");
            Console.WriteLine("    dotnet build -c Release        (Release 모드)");
            Console.WriteLine("    dotnet run -c Release          (Release로 실행)");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 5: 배포 방식
        // ─────────────────────────────────────────────
        static void Lesson5DeploymentMethods()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 5: 배포 방식 — FDD, SCD, AOT");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ FDD (Framework-Dependent Deployment)
              - 대상 서버에 .NET 런타임이 설치되어 있어야 함
              - 배포 파일이 작음
              - 기본 방식

            ★ SCD (Self-Contained Deployment)
              - .NET 런타임을 함께 포함
              - 대상 서버에 .NET 설치 불필요!
              - 배포 파일이 큼 (수십~수백 MB)

            ★ AOT (Ahead-Of-Time) — .NET 8+
              - 네이티브 코드로 컴파일
              - 시작 시간 매우 빠름
              - 제약 사항 있음 (Reflection 제한 등)
            */

            Console.WriteLine("  ┌──────────────────────────────────────────────────┐");
            Console.WriteLine("  │ 배포 방식 비교                                  │");
            Console.WriteLine("  ├──────────┬─────────┬─────────┬─────────┐        │");
            Console.WriteLine("  │          │  FDD    │  SCD    │  AOT    │        │");
            Console.WriteLine("  ├──────────┼─────────┼─────────┼─────────┤        │");
            Console.WriteLine("  │ 런타임   │ 필요    │ 포함    │ 불필요  │        │");
            Console.WriteLine("  │ 파일크기 │ 작음    │ 큼      │ 중간    │        │");
            Console.WriteLine("  │ 시작속도 │ 보통    │ 보통    │ 빠름    │        │");
            Console.WriteLine("  │ 호환성   │ 높음    │ 높음    │ 제한적  │        │");
            Console.WriteLine("  └──────────┴─────────┴─────────┴─────────┘        │");
            Console.WriteLine("  └──────────────────────────────────────────────────┘");
            Console.WriteLine();

            Console.WriteLine("  ★ 배포 명령어:");
            Console.WriteLine("    # FDD (기본)");
            Console.WriteLine("    dotnet publish -c Release -o ./publish");
            Console.WriteLine();
            Console.WriteLine("    # SCD (자체 포함)");
            Console.WriteLine("    dotnet publish -c Release --self-contained -r win-x64 -o ./publish");
            Console.WriteLine();
            Console.WriteLine("    # 단일 파일");
            Console.WriteLine("    dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true");
            Console.WriteLine();
            Console.WriteLine("    # AOT (네이티브)");
            Console.WriteLine("    dotnet publish -c Release -r win-x64 -p:PublishAot=true");
            Console.WriteLine();

            // 배포 매니페스트 작성
            Directory.CreateDirectory(DataFolder);
            string manifestPath = Path.Combine(DataFolder, "deploy-manifest.txt");
            var lines = new List<string>
            {
                "=== 배포 매니페스트 ===",
                $"생성 시각: {DateTime.Now:yyyy-MM-dd HH:mm:ss}",
                "앱 이름: school-management",
                "프레임워크: net8.0",
                "빌드 구성: Release",
                "배포 방식: FDD",
                "환경: Production",
            };
            File.WriteAllLines(manifestPath, lines, Encoding.UTF8);
            Console.WriteLine("  [배포 매니페스트 생성] " + manifestPath);
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 6: 환경별 설정
        // ─────────────────────────────────────────────
        static void Lesson6Configuration()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 6: 환경별 설정 — appsettings, 환경변수");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            Console.WriteLine("  ★ ASP.NET Core 설정 우선순위 (낮은순 → 높은순):");
            Console.WriteLine("    1. appsettings.json              (기본 설정)");
            Console.WriteLine("    2. appsettings.{Environment}.json (환경별 설정)");
            Console.WriteLine("    3. User Secrets                  (개발용 비밀)");
            Console.WriteLine("    4. 환경 변수                     (서버 설정)");
            Console.WriteLine("    5. 명령줄 인자                   (최우선)");
            Console.WriteLine();

            Console.WriteLine("  ★ appsettings.json 예시:");
            Console.WriteLine("    {");
            Console.WriteLine("      \"ConnectionStrings\": {");
            Console.WriteLine("        \"Default\": \"Server=localhost;Database=SchoolDb\"");
            Console.WriteLine("      },");
            Console.WriteLine("      \"Logging\": {");
            Console.WriteLine("        \"LogLevel\": { \"Default\": \"Information\" }");
            Console.WriteLine("      },");
            Console.WriteLine("      \"MaxStudents\": 500");
            Console.WriteLine("    }");
            Console.WriteLine();

            Console.WriteLine("  ★ 환경 변수로 설정 덮어쓰기:");
            Console.WriteLine("    ASPNETCORE_ENVIRONMENT=Production");
            Console.WriteLine("    ConnectionStrings__Default=\"Server=prod-db;...\"");
            Console.WriteLine("    → : 대신 __ (더블 언더스코어) 사용");
            Console.WriteLine();

            // 현재 환경 정보 출력
            Console.WriteLine("  [현재 런타임 정보]");
            Console.WriteLine($"    OS: {Environment.OSVersion}");
            Console.WriteLine($"    .NET: {Environment.Version}");
            Console.WriteLine($"    64비트: {Environment.Is64BitProcess}");
            Console.WriteLine($"    CPU 코어: {Environment.ProcessorCount}");
            Console.WriteLine($"    작업 디렉토리: {Environment.CurrentDirectory}");
            Console.WriteLine();
        }

        // ─────────────────────────────────────────────
        // 레슨 7: CI/CD 기초
        // ─────────────────────────────────────────────
        static void Lesson7CiCd()
        {
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  레슨 7: CI/CD — 자동 빌드와 배포");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine();

            /*
            ★ CI = Continuous Integration (지속적 통합)
              → 코드를 push할 때마다 자동으로 빌드 + 테스트

            ★ CD = Continuous Deployment/Delivery (지속적 배포)
              → 테스트 통과 후 자동으로 서버에 배포
            */

            Console.WriteLine("  ★ CI/CD 파이프라인:");
            Console.WriteLine("    ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐");
            Console.WriteLine("    │  Push  │ → │ Build  │ → │  Test  │ → │ Deploy │");
            Console.WriteLine("    └────────┘   └────────┘   └────────┘   └────────┘");
            Console.WriteLine("        코드          빌드         테스트        배포");
            Console.WriteLine("       업로드       확인         자동 실행    서버 반영");
            Console.WriteLine();

            Console.WriteLine("  ★ GitHub Actions 예시 (.github/workflows/build.yml):");
            Console.WriteLine("    name: Build and Test");
            Console.WriteLine("    on: [push, pull_request]");
            Console.WriteLine("    jobs:");
            Console.WriteLine("      build:");
            Console.WriteLine("        runs-on: ubuntu-latest");
            Console.WriteLine("        steps:");
            Console.WriteLine("          - uses: actions/checkout@v4");
            Console.WriteLine("          - uses: actions/setup-dotnet@v4");
            Console.WriteLine("            with: { dotnet-version: 8.0.x }");
            Console.WriteLine("          - run: dotnet restore");
            Console.WriteLine("          - run: dotnet build --no-restore");
            Console.WriteLine("          - run: dotnet test --no-build");
            Console.WriteLine();

            Console.WriteLine("  ★ 인기 CI/CD 도구:");
            Console.WriteLine("  ┌──────────────────────┬──────────────────────────┐");
            Console.WriteLine("  │ GitHub Actions       │ GitHub 내장, 무료 티어   │");
            Console.WriteLine("  │ Azure DevOps         │ MS 공식, .NET 친화적     │");
            Console.WriteLine("  │ Jenkins              │ 자체 호스팅, 유연함      │");
            Console.WriteLine("  │ GitLab CI            │ GitLab 내장              │");
            Console.WriteLine("  └──────────────────────┴──────────────────────────┘");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine("  C# 17단계: 빌드와 배포");
            Console.WriteLine("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
            Console.WriteLine();

            Lesson1CsprojStructure();
            Lesson2SolutionStructure();
            Lesson3DotnetCli();
            Lesson4DebugVsRelease();
            Lesson5DeploymentMethods();
            Lesson6Configuration();
            Lesson7CiCd();

            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  ★ 정리");
            Console.WriteLine("═══════════════════════════════════════════════════");
            Console.WriteLine("  1. .csproj: 프로젝트 설정 (프레임워크, 패키지)");
            Console.WriteLine("  2. Solution: 여러 프로젝트를 하나로 관리");
            Console.WriteLine("  3. dotnet CLI: new, build, run, test, publish");
            Console.WriteLine("  4. Debug vs Release: 개발용 vs 프로덕션용");
            Console.WriteLine("  5. 배포: FDD, SCD, AOT 세 가지 방식");
            Console.WriteLine("  6. 설정: appsettings.json + 환경변수");
            Console.WriteLine("  7. CI/CD: 자동 빌드 + 테스트 + 배포");
            Console.WriteLine();
        }
    }
}
