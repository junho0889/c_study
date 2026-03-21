# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 17단계: 빌드와 배포
#   ─ 프로젝트 구조, 가상환경, 패키징, 코드 품질, Git, CI/CD, Docker ─
#   ■ 실행 방법: python 17_build_deploy.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 프로젝트 구조 — 표준 레이아웃, src/tests/docs, __main__.py
#   2. 가상환경 관리 — venv, pip, requirements.txt vs pyproject.toml
#   3. 환경 변수와 설정 — os.environ, .env 파일, 설정 클래스 패턴
#   4. 패키징 — setup.py vs pyproject.toml, wheel, entry_points
#   5. 코드 품질 도구 — black, flake8, mypy, isort
#   6. Git 기초 — init, add, commit, branch, merge, .gitignore
#   7. CI/CD 개념 — GitHub Actions 워크플로 구조
#   8. Docker로 배포 — Dockerfile 작성, 이미지 빌드, 컨테이너 실행
#   9. 실전: CLI 도구 패키징하여 배포 준비
#
# ─────────────────────────────────────────────────────────────────────────

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import zipfile
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────
# ■ 공통 헬퍼 함수
# ─────────────────────────────────────────────────────────────────────────

def print_lesson(title: str) -> None:
    """레슨 제목을 눈에 띄게 출력한다."""
    print()
    print("┌──────────────────────────────────────┐")
    print(f"│  {title:<36s} │")
    print("└──────────────────────────────────────┘")
    print()


# =========================================================================
#
#   레슨 1 — 프로젝트 구조
#
# =========================================================================

def lesson1_project_structure():
    print_lesson("레슨 1 : 프로젝트 구조")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 표준 파이썬 프로젝트 레이아웃
    # ─────────────────────────────────────────────────────────────────────
    #
    #   프로젝트를 잘 정리하면:
    #   - 다른 사람이 코드를 쉽게 이해
    #   - 테스트, 배포, 문서화가 편리
    #   - IDE가 자동으로 인식
    #
    #   비유: 옷장 정리
    #     서랍별로 양말, 셔츠, 바지를 나누면 찾기 쉬운 것처럼
    #     코드도 역할별로 폴더를 나누면 관리가 편하다
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 표준 프로젝트 레이아웃")
    print("  ─────────────────────────────────────")
    print("""
  my_project/
  ├── pyproject.toml         # 프로젝트 설정 (빌드, 의존성)
  ├── README.md              # 프로젝트 설명
  ├── LICENSE                # 라이선스
  ├── .gitignore             # Git이 무시할 파일 목록
  ├── .env.example           # 환경 변수 예시
  ├── src/
  │   └── my_package/
  │       ├── __init__.py    # 패키지 초기화
  │       ├── __main__.py    # python -m my_package 실행 진입점
  │       ├── core.py        # 핵심 로직
  │       ├── cli.py         # CLI 인터페이스
  │       └── utils.py       # 유틸리티 함수
  ├── tests/
  │   ├── __init__.py
  │   ├── test_core.py       # 핵심 로직 테스트
  │   └── test_cli.py        # CLI 테스트
  └── docs/
      └── usage.md           # 사용 설명서
    """)

    # ─────────────────────────────────────────────────────────────────────
    # ■ __init__.py의 역할
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "이 폴더는 파이썬 패키지입니다"라고 알려주는 파일
    #   비어 있어도 되고, 패키지를 import할 때 실행될 코드를 넣을 수 있음
    #
    #   예) from my_package import some_function
    #       → __init__.py가 없으면 import 불가!
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ 실제로 프로젝트 구조를 만들어보기
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "my_project"

        # 디렉토리 생성
        (project_dir / "src" / "my_package").mkdir(parents=True)
        (project_dir / "tests").mkdir()
        (project_dir / "docs").mkdir()

        # 파일 생성
        (project_dir / "src" / "my_package" / "__init__.py").write_text(
            '"""My Package — 학습용 패키지"""\n\n__version__ = "1.0.0"\n',
            encoding="utf-8"
        )
        (project_dir / "src" / "my_package" / "__main__.py").write_text(
            'from my_package.core import main\n\nif __name__ == "__main__":\n    main()\n',
            encoding="utf-8"
        )
        (project_dir / "src" / "my_package" / "core.py").write_text(
            'def greet(name: str) -> str:\n    return f"안녕하세요, {name}님!"\n\n'
            'def main():\n    print(greet("세계"))\n',
            encoding="utf-8"
        )
        (project_dir / "tests" / "__init__.py").write_text("", encoding="utf-8")

        # 구조 확인
        print("  ■ 생성된 프로젝트 구조 확인")
        print("  ─────────────────────────────────────")

        for path in sorted(project_dir.rglob("*")):
            rel = path.relative_to(project_dir)
            indent = "    " * len(rel.parts)
            if path.is_dir():
                print(f"  {indent}{path.name}/")
            else:
                size = path.stat().st_size
                print(f"  {indent}{path.name} ({size} bytes)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ __main__.py — 패키지를 직접 실행
    # ─────────────────────────────────────────────────────────────────────
    #
    #   python -m my_package → __main__.py가 실행됨
    #
    #   비유: 폴더에 "대표 전화번호"를 붙여두는 것
    #     패키지(폴더)를 실행하면 __main__.py가 대표로 응답
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ __main__.py의 역할")
    print("  ─────────────────────────────────────")
    print("  python -m my_package  → __main__.py 실행")
    print("  python my_package/    → __main__.py 실행")
    print("  → 패키지를 '프로그램처럼' 실행할 수 있게 해줌")
    print()


# =========================================================================
#
#   레슨 2 — 가상환경 관리
#
# =========================================================================

def lesson2_virtual_environment():
    print_lesson("레슨 2 : 가상환경 관리")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 가상환경(venv)이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   프로젝트별로 독립된 파이썬 환경을 만드는 것
    #
    #   비유: 실험실 각 테이블에 독립된 도구 세트가 있는 것
    #     프로젝트 A: Django 3.2 필요
    #     프로젝트 B: Django 4.0 필요
    #     → 같은 컴퓨터에서 충돌 없이 사용 가능!
    #
    #   왜 필요한가?
    #     1. 프로젝트마다 다른 패키지 버전 사용 가능
    #     2. 시스템 파이썬을 오염시키지 않음
    #     3. 협업 시 같은 환경 재현 가능
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 가상환경 명령어 정리")
    print("  ─────────────────────────────────────")
    print()
    print("  # 1. 가상환경 생성")
    print("  python -m venv .venv")
    print()
    print("  # 2. 가상환경 활성화")
    print("  # Windows:")
    print("  .venv\\Scripts\\activate")
    print("  # macOS/Linux:")
    print("  source .venv/bin/activate")
    print()
    print("  # 3. 패키지 설치")
    print("  pip install requests flask")
    print()
    print("  # 4. 설치된 패키지 확인")
    print("  pip list")
    print("  pip freeze")
    print()
    print("  # 5. requirements.txt 생성")
    print("  pip freeze > requirements.txt")
    print()
    print("  # 6. requirements.txt로 설치")
    print("  pip install -r requirements.txt")
    print()
    print("  # 7. 가상환경 비활성화")
    print("  deactivate")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ requirements.txt vs pyproject.toml
    # ─────────────────────────────────────────────────────────────────────
    #
    #   requirements.txt:
    #     - 단순한 패키지 목록 파일
    #     - 과거 표준, 지금도 많이 사용
    #     - pip freeze > requirements.txt 로 생성
    #
    #   pyproject.toml:
    #     - 현대 파이썬 표준 (PEP 621)
    #     - 패키지 메타데이터 + 빌드 설정 + 의존성을 한 파일에
    #     - pip, poetry, hatch 등 다양한 도구가 지원
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ requirements.txt 예시")
    print("  ─────────────────────────────────────")

    requirements_content = textwrap.dedent("""\
        # 웹 프레임워크
        flask==3.0.0
        # HTTP 요청
        requests>=2.31.0,<3.0.0
        # 데이터 처리
        pandas~=2.1.0
        # 개발용 (테스트, 린트)
        pytest>=7.0.0
        black>=23.0.0
    """)
    print(textwrap.indent(requirements_content, "    "))

    print("  ■ pyproject.toml 예시 (현대 표준)")
    print("  ─────────────────────────────────────")

    pyproject_content = textwrap.dedent("""\
        [project]
        name = "my-awesome-app"
        version = "1.0.0"
        description = "학습용 프로젝트"
        requires-python = ">=3.10"
        dependencies = [
            "flask>=3.0.0",
            "requests>=2.31.0",
        ]

        [project.optional-dependencies]
        dev = ["pytest", "black", "mypy"]

        [project.scripts]
        my-app = "my_package.cli:main"
    """)
    print(textwrap.indent(pyproject_content, "    "))


# =========================================================================
#
#   레슨 3 — 환경 변수와 설정
#
# =========================================================================

def lesson3_environment_variables():
    print_lesson("레슨 3 : 환경 변수와 설정")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 환경 변수란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   운영체제 수준에서 설정하는 변수
    #   코드 변경 없이 동작을 바꿀 수 있다!
    #
    #   비유: TV 리모컨의 "모드" 버튼
    #     같은 TV(코드)인데 모드(환경변수)에 따라
    #     영화 모드 / 게임 모드 / 표준 모드로 동작이 바뀜
    #
    #   활용 예:
    #     DATABASE_URL = "postgresql://localhost/mydb"
    #     SECRET_KEY = "super-secret-key"
    #     DEBUG = "true"
    #
    #   ★ 중요: 비밀 정보(API 키, DB 비밀번호)는 절대 코드에 직접 쓰지 말 것!
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ os.environ으로 환경 변수 읽기
    print("  ■ 환경 변수 읽기 (os.environ)")
    print("  ─────────────────────────────────────")

    # 있는 변수 읽기
    path = os.environ.get("PATH", "없음")
    print(f"  PATH 환경 변수 (앞 50자): {path[:50]}...")
    print()

    # 없는 변수에 기본값 설정
    db_host = os.environ.get("DATABASE_HOST", "localhost")
    db_port = int(os.environ.get("DATABASE_PORT", "5432"))
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    print(f"  DATABASE_HOST: {db_host} (기본값)")
    print(f"  DATABASE_PORT: {db_port} (기본값)")
    print(f"  DEBUG: {debug} (기본값)")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 설정 클래스 패턴 — 환경 변수를 체계적으로 관리
    # ─────────────────────────────────────────────────────────────────────

    class AppConfig:
        """환경 변수를 클래스로 관리하는 패턴"""
        def __init__(self):
            self.app_name = os.environ.get("APP_NAME", "my-app")
            self.debug = os.environ.get("DEBUG", "false").lower() == "true"
            self.port = int(os.environ.get("PORT", "8000"))
            self.database_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
            self.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

        def __repr__(self):
            return (f"AppConfig(app_name='{self.app_name}', "
                    f"debug={self.debug}, port={self.port})")

        def validate(self):
            """설정값 유효성 검사"""
            errors = []
            if self.secret_key == "change-me-in-production":
                errors.append("SECRET_KEY를 변경해주세요!")
            if self.port < 1 or self.port > 65535:
                errors.append(f"유효하지 않은 포트: {self.port}")
            return errors

    print("  ■ 설정 클래스 패턴")
    print("  ─────────────────────────────────────")

    config = AppConfig()
    print(f"  설정: {config}")
    warnings = config.validate()
    if warnings:
        for w in warnings:
            print(f"  경고: {w}")
    print()

    # ■ .env 파일 수동 파싱
    print("  ■ .env 파일 파싱 (직접 구현)")
    print("  ─────────────────────────────────────")

    def parse_env_file(content: str) -> dict:
        """간단한 .env 파서"""
        env = {}
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                # 따옴표 제거
                value = value.strip().strip('"').strip("'")
                env[key.strip()] = value
        return env

    env_content = textwrap.dedent("""\
        # 개발 환경 설정
        APP_NAME=school-manager
        DEBUG=true
        PORT=3000
        DATABASE_URL="sqlite:///dev.db"
        SECRET_KEY='dev-secret-key-123'
    """)

    parsed = parse_env_file(env_content)
    for key, value in parsed.items():
        print(f"    {key} = {value}")
    print()


# =========================================================================
#
#   레슨 4 — 패키징
#
# =========================================================================

def lesson4_packaging():
    print_lesson("레슨 4 : 패키징")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 패키징이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   코드를 다른 사람이 쉽게 설치하고 사용할 수 있도록
    #   하나의 배포 가능한 패키지로 묶는 것
    #
    #   비유: 요리를 해서 "밀키트"로 포장하는 것
    #     재료(코드) + 레시피(설정) + 포장(배포 형식)
    #     → 누구나 쉽게 조리(설치)할 수 있다!
    #
    #   pip install my-package → 이렇게 설치 가능하게 만드는 과정
    #
    # ─────────────────────────────────────────────────────────────────────

    # ■ pyproject.toml 상세 구조
    print("  ■ pyproject.toml 상세 구조")
    print("  ─────────────────────────────────────")

    pyproject = textwrap.dedent("""\
        [build-system]
        requires = ["setuptools>=68.0", "wheel"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "student-manager"
        version = "1.0.0"
        description = "학생 성적 관리 CLI 도구"
        readme = "README.md"
        license = {text = "MIT"}
        requires-python = ">=3.10"
        authors = [
            {name = "홍길동", email = "hong@example.com"}
        ]
        dependencies = [
            "click>=8.0.0",
        ]

        [project.optional-dependencies]
        dev = ["pytest>=7.0", "black", "mypy"]

        [project.scripts]
        student-mgr = "student_manager.cli:main"
    """)
    print(textwrap.indent(pyproject, "    "))

    # ─────────────────────────────────────────────────────────────────────
    # ■ 빌드 형식: sdist vs wheel
    # ─────────────────────────────────────────────────────────────────────
    #
    #   sdist (Source Distribution):
    #     - 소스 코드 그대로 압축 (.tar.gz)
    #     - 설치 시 빌드 과정이 필요할 수 있음
    #
    #   wheel (.whl):
    #     - 미리 빌드된 바이너리 패키지
    #     - 설치가 빠르다! (빌드 과정 불필요)
    #     - 사실상 zip 파일 (확장자만 .whl)
    #
    #   빌드 명령:
    #     python -m build          # sdist + wheel 모두 생성
    #     python -m build --wheel  # wheel만 생성
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 빌드 형식 비교")
    print("  ─────────────────────────────────────")
    print("  sdist (.tar.gz)  → 소스 코드 압축 (설치 시 빌드 필요)")
    print("  wheel (.whl)     → 미리 빌드됨 (빌드 빠름, 권장!)")
    print()

    # ■ entry_points — CLI 명령어 등록
    print("  ■ entry_points - CLI 명령어 등록")
    print("  ─────────────────────────────────────")
    print('  [project.scripts]')
    print('  student-mgr = "student_manager.cli:main"')
    print()
    print("  → pip install 후 터미널에서 'student-mgr' 명령어 사용 가능!")
    print("  → student_manager/cli.py 의 main() 함수가 실행됨")
    print()

    # ■ 실제 패키지 빌드 시뮬레이션
    print("  ■ 패키지 빌드 시뮬레이션")
    print("  ─────────────────────────────────────")

    with tempfile.TemporaryDirectory() as temp_dir:
        pkg_dir = Path(temp_dir) / "student_manager"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text('__version__ = "1.0.0"\n', encoding="utf-8")
        (pkg_dir / "core.py").write_text('def hello(): return "Hello"\n', encoding="utf-8")

        # zip으로 간단한 wheel 시뮬레이션
        dist_dir = Path(temp_dir) / "dist"
        dist_dir.mkdir()
        whl_path = dist_dir / "student_manager-1.0.0-py3-none-any.whl"

        with zipfile.ZipFile(whl_path, "w") as zf:
            for py_file in pkg_dir.glob("*.py"):
                zf.write(py_file, arcname=f"student_manager/{py_file.name}")

        print(f"  생성된 파일: {whl_path.name}")
        print(f"  파일 크기: {whl_path.stat().st_size} bytes")

        with zipfile.ZipFile(whl_path, "r") as zf:
            print(f"  포함된 파일: {zf.namelist()}")
    print()


# =========================================================================
#
#   레슨 5 — 코드 품질 도구
#
# =========================================================================

def lesson5_code_quality():
    print_lesson("레슨 5 : 코드 품질 도구")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 코드 품질 도구가 필요한가?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   혼자 코딩: 내 스타일대로 편하게
    #   팀 코딩:   모두 다른 스타일 → 읽기 어렵고 버그 발생
    #
    #   해결: 자동화된 도구로 스타일/품질을 통일!
    #
    #   비유: 원고 교정 과정
    #     - 포맷터(black) = 편집자가 문장 형식을 통일
    #     - 린터(flake8) = 교정자가 맞춤법/문법 오류 지적
    #     - 타입체커(mypy) = 사실 확인자가 내용 검증
    #     - 정렬기(isort) = 참고문헌을 가나다순으로 정리
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ 주요 코드 품질 도구 비교")
    print("  ─────────────────────────────────────")
    print()
    print("  도구       │ 역할          │ 명령어 예시")
    print("  ──────────┼──────────────┼────────────────────")
    print("  black      │ 코드 포맷터   │ black src/")
    print("  flake8     │ 스타일 린터   │ flake8 src/")
    print("  mypy       │ 타입 체커     │ mypy src/")
    print("  isort      │ import 정렬   │ isort src/")
    print("  ruff       │ 통합 린터     │ ruff check src/")
    print()

    # ■ black 포맷터 — 코드 스타일 통일
    print("  ■ black - 코드 포맷터")
    print("  ─────────────────────────────────────")

    before_black = textwrap.dedent("""\
        x = {  'a':37,'b':42,
        'c':    927}
        y = 'hello ''world'
        if very_long_variable_name is not None and another_variable is not None and third_variable is not None:
            pass
    """)

    after_black = textwrap.dedent("""\
        x = {"a": 37, "b": 42, "c": 927}
        y = "hello " "world"
        if (
            very_long_variable_name is not None
            and another_variable is not None
            and third_variable is not None
        ):
            pass
    """)

    print("  변환 전:")
    print(textwrap.indent(before_black, "    "))
    print("  변환 후 (black 적용):")
    print(textwrap.indent(after_black, "    "))

    # ■ flake8 린터 — 스타일 검사
    print("  ■ flake8 - 스타일 린터")
    print("  ─────────────────────────────────────")
    print("  자주 나오는 경고:")
    print("    E302: 함수 사이 빈 줄이 2줄 미만")
    print("    E501: 줄 길이 80자 초과")
    print("    W291: 줄 끝에 불필요한 공백")
    print("    F401: import 했지만 사용하지 않은 모듈")
    print("    F841: 변수를 만들었지만 사용하지 않음")
    print()

    # ■ mypy 타입 체커
    print("  ■ mypy - 타입 체커")
    print("  ─────────────────────────────────────")

    type_example = textwrap.dedent("""\
        def add(a: int, b: int) -> int:
            return a + b

        result = add(1, "2")  # mypy 에러: str은 int가 아님!
    """)
    print(textwrap.indent(type_example, "    "))
    print("  → mypy가 실행 전에 타입 오류를 잡아줌!")
    print()


# =========================================================================
#
#   레슨 6 — Git 기초
#
# =========================================================================

def lesson6_git_basics():
    print_lesson("레슨 6 : Git 기초")

    # ─────────────────────────────────────────────────────────────────────
    # ■ Git이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   코드의 변경 이력을 추적하는 버전 관리 도구
    #
    #   비유: 문서의 "변경 추적" 기능 (Word의 Track Changes)
    #     - 누가, 언제, 무엇을 바꿨는지 기록
    #     - 과거 버전으로 되돌리기 가능
    #     - 여러 사람이 동시에 작업 후 합치기 가능
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ Git 핵심 명령어")
    print("  ─────────────────────────────────────")
    print()

    git_commands = [
        ("git init",           "새 저장소 생성"),
        ("git clone URL",      "원격 저장소 복제"),
        ("git status",         "현재 상태 확인"),
        ("git add 파일",       "변경 파일을 스테이징"),
        ("git add .",          "모든 변경 파일 스테이징"),
        ("git commit -m '메시지'", "스테이징된 변경 커밋"),
        ("git log --oneline",  "커밋 이력 확인"),
        ("git diff",           "변경 내용 비교"),
        ("git branch 이름",   "새 브랜치 생성"),
        ("git checkout 이름", "브랜치 전환"),
        ("git merge 이름",    "브랜치 합치기"),
        ("git push",           "원격 저장소에 업로드"),
        ("git pull",           "원격 저장소에서 다운로드"),
    ]

    for cmd, desc in git_commands:
        print(f"    {cmd:<30s}  # {desc}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ .gitignore — Git이 무시할 파일
    # ─────────────────────────────────────────────────────────────────────
    #
    #   추적하지 않아야 할 파일:
    #     - __pycache__/    → 컴파일된 캐시
    #     - .venv/          → 가상환경
    #     - .env            → 비밀 정보
    #     - *.pyc           → 바이트코드
    #     - dist/           → 빌드 산출물
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ .gitignore 예시 (Python 프로젝트)")
    print("  ─────────────────────────────────────")

    gitignore = textwrap.dedent("""\
        # 가상환경
        .venv/
        venv/

        # 파이썬 캐시
        __pycache__/
        *.pyc
        *.pyo

        # 빌드 산출물
        dist/
        build/
        *.egg-info/

        # 환경 변수 (비밀 정보!)
        .env

        # IDE 설정
        .vscode/
        .idea/

        # OS 파일
        .DS_Store
        Thumbs.db
    """)
    print(textwrap.indent(gitignore, "    "))

    # ■ 브랜치 전략
    print("  ■ Git 브랜치 전략 (Git Flow 간소화)")
    print("  ─────────────────────────────────────")
    print("  main     ─────●─────────●───────●──── 배포 버전")
    print("                │         ↑       ↑")
    print("  develop  ─────●────●────●───●───●──── 개발 통합")
    print("                     │        │")
    print("  feature  ──────────●────────●──────── 기능 개발")
    print()
    print("  main: 항상 배포 가능한 안정 버전")
    print("  develop: 다음 릴리즈를 위한 개발 브랜치")
    print("  feature: 기능별 개발 브랜치 (develop에서 분기)")
    print()


# =========================================================================
#
#   레슨 7 — CI/CD 개념
#
# =========================================================================

def lesson7_ci_cd():
    print_lesson("레슨 7 : CI/CD 개념")

    # ─────────────────────────────────────────────────────────────────────
    # ■ CI/CD란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   CI (Continuous Integration): 지속적 통합
    #     코드를 커밋할 때마다 자동으로 빌드 + 테스트
    #     "내가 코드를 합치면 자동으로 검사해줘!"
    #
    #   CD (Continuous Deployment): 지속적 배포
    #     테스트 통과 후 자동으로 서버에 배포
    #     "검사 통과하면 자동으로 출시해줘!"
    #
    #   비유: 자동차 공장
    #     CI = 부품 조립 후 자동 품질 검사
    #     CD = 검사 통과하면 자동으로 출고
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ CI/CD 파이프라인 흐름")
    print("  ─────────────────────────────────────")
    print("  코드 푸시 → 자동 빌드 → 자동 테스트 → 자동 배포")
    print("     ↑                        │")
    print("     └── 실패 시 알림 ←───────┘")
    print()

    # ■ GitHub Actions 워크플로 예시
    print("  ■ GitHub Actions 워크플로 예시")
    print("  ─────────────────────────────────────")

    workflow = textwrap.dedent("""\
        # .github/workflows/ci.yml
        name: CI Pipeline

        on:
          push:
            branches: [main, develop]
          pull_request:
            branches: [main]

        jobs:
          test:
            runs-on: ubuntu-latest
            strategy:
              matrix:
                python-version: ["3.10", "3.11", "3.12"]

            steps:
              - uses: actions/checkout@v4

              - name: Set up Python
                uses: actions/setup-python@v5
                with:
                  python-version: ${{ matrix.python-version }}

              - name: Install dependencies
                run: |
                  python -m pip install --upgrade pip
                  pip install -r requirements.txt
                  pip install pytest black flake8 mypy

              - name: Format check (black)
                run: black --check src/

              - name: Lint (flake8)
                run: flake8 src/

              - name: Type check (mypy)
                run: mypy src/

              - name: Test (pytest)
                run: pytest tests/ -v
    """)
    print(textwrap.indent(workflow, "    "))

    # ■ GitHub Actions 주요 개념
    print("  ■ GitHub Actions 핵심 개념")
    print("  ─────────────────────────────────────")
    print("  on:      → 언제 실행? (push, PR 등)")
    print("  jobs:    → 어떤 작업들? (test, build, deploy)")
    print("  steps:   → 각 작업의 세부 단계")
    print("  matrix:  → 여러 환경에서 동시 테스트 (Python 3.10, 3.11, 3.12)")
    print("  secrets: → 비밀 정보 (API 키, 토큰 등)")
    print()


# =========================================================================
#
#   레슨 8 — Docker로 배포
#
# =========================================================================

def lesson8_docker():
    print_lesson("레슨 8 : Docker로 배포")

    # ─────────────────────────────────────────────────────────────────────
    # ■ Docker란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   애플리케이션을 "컨테이너"라는 격리된 환경에서 실행하는 도구
    #
    #   비유: 이사할 때 물건을 "컨테이너 박스"에 넣는 것
    #     - 박스 안에 필요한 것이 다 들어있음 (파이썬, 라이브러리, 코드)
    #     - 어디로 보내든 박스를 열면 바로 사용 가능
    #     - "내 컴퓨터에서는 되는데..." 문제가 사라짐!
    #
    #   핵심 개념:
    #     이미지(Image): 컨테이너의 설계도 (Dockerfile로 생성)
    #     컨테이너(Container): 이미지로 만든 실행 인스턴스
    #     Dockerfile: 이미지를 만드는 레시피
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ Docker 핵심 명령어")
    print("  ─────────────────────────────────────")

    docker_commands = [
        ("docker build -t my-app .",        "이미지 빌드"),
        ("docker run my-app",               "컨테이너 실행"),
        ("docker run -p 8000:8000 my-app",  "포트 매핑하여 실행"),
        ("docker run -d my-app",            "백그라운드 실행"),
        ("docker ps",                       "실행 중인 컨테이너 목록"),
        ("docker stop 컨테이너ID",          "컨테이너 중지"),
        ("docker images",                   "로컬 이미지 목록"),
        ("docker push my-app:latest",       "이미지를 레지스트리에 업로드"),
    ]

    for cmd, desc in docker_commands:
        print(f"    {cmd:<40s}  # {desc}")
    print()

    # ■ Dockerfile 작성법
    print("  ■ Dockerfile 예시 (파이썬 프로젝트)")
    print("  ─────────────────────────────────────")

    dockerfile = textwrap.dedent("""\
        # 1. 베이스 이미지 선택 (가벼운 slim 버전)
        FROM python:3.12-slim

        # 2. 작업 디렉토리 설정
        WORKDIR /app

        # 3. 의존성 먼저 설치 (캐시 활용!)
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # 4. 소스 코드 복사
        COPY src/ ./src/

        # 5. 환경 변수 설정
        ENV APP_NAME=student-manager
        ENV PORT=8000

        # 6. 포트 노출
        EXPOSE 8000

        # 7. 실행 명령
        CMD ["python", "-m", "src.main"]
    """)
    print(textwrap.indent(dockerfile, "    "))

    # ─────────────────────────────────────────────────────────────────────
    # ■ Dockerfile 최적화 팁
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1. 레이어 캐싱: 자주 바뀌는 것을 아래에 배치
    #      requirements.txt → 잘 안 바뀜 → 위에
    #      소스 코드          → 자주 바뀜 → 아래에
    #
    #   2. slim 이미지 사용: python:3.12-slim (800MB → 150MB)
    #
    #   3. .dockerignore: 불필요한 파일 제외
    #      .venv/ .git/ __pycache__/ .env
    #
    #   4. multi-stage build: 빌드와 실행 이미지 분리
    #
    # ─────────────────────────────────────────────────────────────────────

    print("  ■ .dockerignore 예시")
    print("  ─────────────────────────────────────")
    dockerignore = textwrap.dedent("""\
        .venv/
        .git/
        __pycache__/
        .env
        *.pyc
        tests/
        docs/
    """)
    print(textwrap.indent(dockerignore, "    "))

    # ■ Docker Compose
    print("  ■ docker-compose.yml 예시 (여러 서비스)")
    print("  ─────────────────────────────────────")

    compose = textwrap.dedent("""\
        version: "3.8"
        services:
          app:
            build: .
            ports:
              - "8000:8000"
            environment:
              - DATABASE_URL=postgresql://db:5432/mydb
            depends_on:
              - db

          db:
            image: postgres:15
            environment:
              POSTGRES_DB: mydb
              POSTGRES_PASSWORD: secret
            volumes:
              - pgdata:/var/lib/postgresql/data

        volumes:
          pgdata:
    """)
    print(textwrap.indent(compose, "    "))


# =========================================================================
#
#   레슨 9 — 실전: CLI 도구 패키징하여 배포 준비
#
# =========================================================================

def lesson9_cli_packaging():
    print_lesson("레슨 9 : CLI 도구 패키징 실전")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시나리오: 성적 계산기 CLI 도구를 만들어 배포 준비
    # ─────────────────────────────────────────────────────────────────────

    with tempfile.TemporaryDirectory() as temp_dir:
        project = Path(temp_dir) / "grade_calc"
        src = project / "src" / "grade_calc"
        tests = project / "tests"

        src.mkdir(parents=True)
        tests.mkdir(parents=True)

        # ■ 1. 핵심 모듈 (core.py)
        core_code = textwrap.dedent('''\
            """성적 계산 핵심 로직"""

            def calculate_average(scores: list[float]) -> float:
                """점수 리스트의 평균을 계산한다."""
                if not scores:
                    raise ValueError("점수가 비어있습니다!")
                return sum(scores) / len(scores)

            def determine_grade(average: float) -> str:
                """평균 점수를 학점으로 변환한다."""
                if average >= 90:
                    return "A"
                elif average >= 80:
                    return "B"
                elif average >= 70:
                    return "C"
                elif average >= 60:
                    return "D"
                return "F"

            def format_report(name: str, scores: dict[str, float]) -> str:
                """성적표 문자열을 생성한다."""
                lines = [f"=== {name}의 성적표 ==="]
                for subject, score in scores.items():
                    lines.append(f"  {subject}: {score}점")
                avg = calculate_average(list(scores.values()))
                grade = determine_grade(avg)
                lines.append(f"  평균: {avg:.1f}점 ({grade})")
                return "\\n".join(lines)
        ''')
        (src / "core.py").write_text(core_code, encoding="utf-8")

        # ■ 2. CLI 모듈 (cli.py)
        cli_code = textwrap.dedent('''\
            """CLI 인터페이스"""
            import sys
            from .core import calculate_average, determine_grade

            def main():
                if len(sys.argv) < 2:
                    print("사용법: grade-calc 점수1 점수2 ...")
                    sys.exit(1)
                try:
                    scores = [float(s) for s in sys.argv[1:]]
                    avg = calculate_average(scores)
                    grade = determine_grade(avg)
                    print(f"평균: {avg:.1f}점, 학점: {grade}")
                except ValueError as e:
                    print(f"오류: {e}")
                    sys.exit(1)
        ''')
        (src / "cli.py").write_text(cli_code, encoding="utf-8")

        # ■ 3. __init__.py, __main__.py
        (src / "__init__.py").write_text('__version__ = "1.0.0"\n', encoding="utf-8")
        (src / "__main__.py").write_text(
            'from .cli import main\nmain()\n', encoding="utf-8"
        )

        # ■ 4. 테스트 (test_core.py)
        test_code = textwrap.dedent('''\
            """핵심 로직 테스트"""
            import unittest
            import sys
            sys.path.insert(0, "src")
            from grade_calc.core import calculate_average, determine_grade

            class TestGradeCalc(unittest.TestCase):
                def test_average(self):
                    self.assertEqual(calculate_average([80, 90, 100]), 90.0)

                def test_average_empty(self):
                    with self.assertRaises(ValueError):
                        calculate_average([])

                def test_grade_a(self):
                    self.assertEqual(determine_grade(95), "A")

                def test_grade_f(self):
                    self.assertEqual(determine_grade(50), "F")

            if __name__ == "__main__":
                unittest.main()
        ''')
        (tests / "test_core.py").write_text(test_code, encoding="utf-8")
        (tests / "__init__.py").write_text("", encoding="utf-8")

        # ■ 5. pyproject.toml
        pyproject_content = textwrap.dedent('''\
            [build-system]
            requires = ["setuptools>=68.0", "wheel"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "grade-calc"
            version = "1.0.0"
            description = "성적 계산 CLI 도구"
            requires-python = ">=3.10"

            [project.scripts]
            grade-calc = "grade_calc.cli:main"
        ''')
        (project / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")

        # ■ 6. 프로젝트 구조 출력
        print("  ■ 생성된 CLI 도구 프로젝트 구조")
        print("  ─────────────────────────────────────")

        for path in sorted(project.rglob("*")):
            if path.is_file():
                rel = path.relative_to(project)
                print(f"    {rel}")
        print()

        # ■ 7. 빌드 산출물 생성 (zip 시뮬레이션)
        print("  ■ 배포 패키지 생성")
        print("  ─────────────────────────────────────")

        dist = project / "dist"
        dist.mkdir()
        zip_path = dist / "grade-calc-1.0.0.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            for py_file in src.glob("*.py"):
                zf.write(py_file, arcname=f"grade_calc/{py_file.name}")
            zf.write(project / "pyproject.toml", arcname="pyproject.toml")

        print(f"  패키지 파일: {zip_path.name}")
        print(f"  크기: {zip_path.stat().st_size} bytes")

        with zipfile.ZipFile(zip_path, "r") as zf:
            print(f"  내용물: {zf.namelist()}")
        print()

    # ■ 배포 체크리스트
    print("  ■ 배포 전 체크리스트")
    print("  ─────────────────────────────────────")
    checklist = [
        "[ ] 모든 테스트 통과 (pytest)",
        "[ ] 코드 포맷 검사 (black --check)",
        "[ ] 린트 통과 (flake8)",
        "[ ] 타입 검사 통과 (mypy)",
        "[ ] requirements.txt / pyproject.toml 업데이트",
        "[ ] 버전 번호 업데이트",
        "[ ] CHANGELOG 작성",
        "[ ] .env 파일이 .gitignore에 포함",
        "[ ] README 업데이트",
        "[ ] 빌드 테스트 (python -m build)",
    ]
    for item in checklist:
        print(f"    {item}")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행 함수
# ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 72)
    print("  파이썬 학습 17단계: 빌드와 배포")
    print("=" * 72)

    lesson1_project_structure()
    lesson2_virtual_environment()
    lesson3_environment_variables()
    lesson4_packaging()
    lesson5_code_quality()
    lesson6_git_basics()
    lesson7_ci_cd()
    lesson8_docker()
    lesson9_cli_packaging()

    print()
    print("=" * 72)
    print("  모든 레슨 완료!")
    print("=" * 72)


if __name__ == "__main__":
    main()
