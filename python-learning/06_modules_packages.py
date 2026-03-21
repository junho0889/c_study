# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 06단계: 모듈과 패키지 완전정복
#   ─ import, 표준 라이브러리, datetime, json/csv, 정규표현식, 패키지 ─
#
#   이 파일 하나로 파이썬 모듈 시스템과 핵심 표준 라이브러리를 마스터합니다.
#   코드를 직접 타이핑하고, 값을 바꿔보면서 실험하세요!
#
#   ■ 실행 방법 (터미널에 입력)
#     python 06_modules_packages.py
#
#   ■ 모듈이란?
#     하나의 .py 파일 = 하나의 모듈!
#     C++ : #include <iostream>
#     파이썬: import os
#     → 파이썬은 모듈 시스템이 훨씬 유연합니다!
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. import 완전정복
#   2. 표준 라이브러리 핵심 (os, sys, pathlib, shutil)
#   3. datetime 완전정복
#   4. json/csv 다루기
#   5. re(정규표현식) 기초
#   6. 패키지 만들기
#   7. pip와 가상환경
#   8. 유용한 내장 함수 총정리
#
# ─────────────────────────────────────────────────────────────────────────

import csv
import io
import json
import math
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


def lesson1_import():
    # =========================================================================
    #
    #   레슨 1 — import 완전정복
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : import 완전정복            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ import의 여러 가지 방법
    # ─────────────────────────────────────────────────────────────────────
    #
    #   1. import 모듈           → 모듈 전체를 가져옴
    #   2. from 모듈 import 이름 → 특정 이름만 가져옴
    #   3. import 모듈 as 별명   → 별명으로 사용
    #   4. from 모듈 import *    → 전부 가져옴 (비추천!)
    #
    #   비유:
    #   1번 = 공구함 전체를 가져옴 (쓸 때 "공구함.망치")
    #   2번 = 망치만 꺼내옴 (그냥 "망치")
    #   3번 = "공구함"을 "도구"라고 이름 바꿔서 가져옴
    #   4번 = 공구함을 쏟아부음 (뭐가 뭔지 헷갈림!)
    #
    #   C++ : #include <math.h>  → 전부 포함
    #   파이썬: 필요한 것만 골라서 가져올 수 있음!
    #

    # 방법 1: import 모듈
    import statistics
    data = [10, 20, 30, 40, 50]
    print(f"  평균 (statistics.mean): {statistics.mean(data)}")

    # 방법 2: from 모듈 import 이름
    from random import randint, choice
    print(f"  랜덤 정수 (1~10): {randint(1, 10)}")
    print(f"  랜덤 선택: {choice(['사과', '바나나', '체리'])}")

    # 방법 3: import as (별명)
    import collections as col
    counter = col.Counter("hello world")
    print(f"  Counter (as 별명): {counter.most_common(3)}")

    # 방법 4: from ... import * (비추천!)
    # from math import *  ← 모든 이름을 현재 네임스페이스에 풀어놓음
    # 문제점: 어떤 이름이 어디서 온 건지 모름 + 이름 충돌 위험!
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ __all__ — import *를 제어하기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   모듈 파일에 __all__ = ["func1", "func2"] 를 정의하면
    #   from 모듈 import * 할 때 __all__에 있는 것만 가져옵니다.
    #
    #   예시:
    #   # mymodule.py
    #   __all__ = ["public_func"]
    #   def public_func(): ...
    #   def _internal_func(): ...   # import *로 안 가져와짐
    #
    print("  __all__: import *의 범위를 제한하는 리스트")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ __name__ == "__main__" 패턴
    # ─────────────────────────────────────────────────────────────────────
    #
    #   이 파일을 직접 실행하면: __name__ = "__main__"
    #   다른 파일이 import하면:  __name__ = "파일이름"
    #
    #   비유: "내가 주인공이면(직접 실행) 이 코드 실행,
    #          조연이면(import됨) 이 코드 건너뜀"
    #
    print(f"  현재 __name__: {__name__}")
    print("  ★ if __name__ == '__main__': 는 거의 모든 파이썬 파일에 넣으세요!")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 모듈 검색 순서
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파이썬이 모듈을 찾는 순서:
    #   1. 현재 디렉토리
    #   2. 환경변수 PYTHONPATH
    #   3. 표준 라이브러리
    #   4. site-packages (pip로 설치한 패키지)
    #
    #   sys.path에서 확인 가능!
    #
    print("  모듈 검색 경로 (처음 3개):")
    for p in sys.path[:3]:
        print(f"    {p}")
    print()


def lesson2_stdlib_files():
    # =========================================================================
    #
    #   레슨 2 — 표준 라이브러리 핵심 (파일/디렉토리)
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : os, sys, pathlib, shutil   │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ os 모듈 — 운영체제와 대화하기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 컴퓨터의 집사! 파일, 폴더, 환경 정보를 관리
    #
    print(f"  현재 작업 디렉토리: {os.getcwd()}")
    print(f"  운영체제: {os.name}")           # 'nt' (Windows) or 'posix' (Linux/Mac)
    print(f"  CPU 코어 수: {os.cpu_count()}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ os.path — 경로 다루기 (전통적 방법)
    # ─────────────────────────────────────────────────────────────────────
    path1 = os.path.join("home", "user", "documents")
    print(f"  경로 합치기: {path1}")
    print(f"  현재 파일: {os.path.basename(__file__)}")
    print(f"  현재 디렉토리: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"  파일 확장자: {os.path.splitext(__file__)}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ pathlib — 경로 다루기 (모던 방법! 추천!)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   os.path보다 직관적이고 객체지향적입니다!
    #   Python 3.4+에서 사용 가능
    #
    #   비유: os.path = 주소를 문자열로 적기
    #         pathlib = 주소를 네비게이션에 넣기
    #
    current = Path(__file__).resolve()
    print(f"  현재 파일 (Path): {current}")
    print(f"  파일 이름: {current.name}")
    print(f"  확장자: {current.suffix}")
    print(f"  확장자 없는 이름: {current.stem}")
    print(f"  부모 디렉토리: {current.parent}")
    print(f"  존재 여부: {current.exists()}")
    print(f"  파일인지: {current.is_file()}")
    print()

    # Path 합치기 (/ 연산자!)
    docs = Path("home") / "user" / "documents"
    print(f"  Path 합치기: {docs}")

    # 임시 디렉토리에서 파일 조작 실습
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 디렉토리 만들기
        new_dir = tmp / "my_folder" / "sub_folder"
        new_dir.mkdir(parents=True)     # parents=True: 중간 폴더도 생성
        print(f"  디렉토리 생성: {new_dir.exists()}")

        # 파일 쓰기/읽기
        file_path = new_dir / "hello.txt"
        file_path.write_text("안녕하세요, pathlib!", encoding="utf-8")
        content = file_path.read_text(encoding="utf-8")
        print(f"  파일 내용: {content}")

        # glob으로 파일 찾기
        (tmp / "test1.py").write_text("# test1", encoding="utf-8")
        (tmp / "test2.py").write_text("# test2", encoding="utf-8")
        (tmp / "data.csv").write_text("a,b", encoding="utf-8")

        py_files = list(tmp.glob("*.py"))
        print(f"  .py 파일들: {[f.name for f in py_files]}")

        # 재귀 glob
        all_files = list(tmp.rglob("*.*"))
        print(f"  모든 파일 (재귀): {[f.name for f in all_files]}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ sys 모듈 — 파이썬 인터프리터 정보
    # ─────────────────────────────────────────────────────────────────────
    print(f"  파이썬 버전: {sys.version}")
    print(f"  플랫폼: {sys.platform}")
    print(f"  실행 인자: {sys.argv[:2]}")
    print(f"  최대 정수: {sys.maxsize}")
    print()


def lesson3_datetime():
    # =========================================================================
    #
    #   레슨 3 — datetime 완전정복
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : datetime 완전정복          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ date, time, datetime 기본
    # ─────────────────────────────────────────────────────────────────────
    #
    #   date     : 날짜만 (2026-03-21)
    #   time     : 시간만 (14:30:00)
    #   datetime : 날짜+시간 (2026-03-21 14:30:00)
    #
    #   비유: date = 달력, time = 시계, datetime = 달력 + 시계
    #
    #   C++ : <chrono> 라이브러리 (훨씬 복잡!)
    #   파이썬: datetime 모듈로 간단하게!
    #

    # 오늘/현재
    today = date.today()
    now = datetime.now()
    print(f"  오늘 날짜: {today}")
    print(f"  현재 시간: {now}")
    print()

    # 직접 생성
    birthday = date(2000, 5, 15)
    meeting = datetime(2026, 3, 21, 14, 30, 0)
    lunch = time(12, 0, 0)

    print(f"  생일: {birthday}")
    print(f"  회의: {meeting}")
    print(f"  점심: {lunch}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 날짜 속성 접근
    # ─────────────────────────────────────────────────────────────────────
    print(f"  년: {now.year}")
    print(f"  월: {now.month}")
    print(f"  일: {now.day}")
    print(f"  시: {now.hour}")
    print(f"  분: {now.minute}")
    print(f"  요일: {now.weekday()}")  # 0=월, 1=화, ..., 6=일
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    print(f"  요일 이름: {weekdays[now.weekday()]}요일")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ timedelta — 날짜/시간 계산
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: "3일 후", "일주일 전"처럼 날짜를 더하고 빼기!
    #
    tomorrow = today + timedelta(days=1)
    last_week = today - timedelta(weeks=1)
    in_100_days = today + timedelta(days=100)

    print(f"  내일: {tomorrow}")
    print(f"  지난주: {last_week}")
    print(f"  100일 후: {in_100_days}")

    # 두 날짜 사이의 차이
    new_year = date(2027, 1, 1)
    diff = new_year - today
    print(f"  새해까지: {diff.days}일 남음")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ strftime / strptime — 포맷 변환
    # ─────────────────────────────────────────────────────────────────────
    #
    #   strftime: datetime → 문자열 (f = format)
    #   strptime: 문자열 → datetime (p = parse)
    #
    #   주요 포맷 코드:
    #   %Y = 4자리 연도    %m = 2자리 월     %d = 2자리 일
    #   %H = 24시간        %M = 분           %S = 초
    #   %A = 요일 이름     %B = 월 이름      %p = AM/PM
    #

    # datetime → 문자열
    formatted = now.strftime("%Y년 %m월 %d일 %H시 %M분")
    print(f"  포맷팅: {formatted}")

    iso = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"  ISO 형식: {iso}")

    # 문자열 → datetime
    date_str = "2026-03-21 14:30:00"
    parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    print(f"  파싱 결과: {parsed}")
    print(f"  타입: {type(parsed)}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ timezone — 시간대 다루기
    # ─────────────────────────────────────────────────────────────────────
    utc_now = datetime.now(timezone.utc)
    kst = timezone(timedelta(hours=9))
    kst_now = datetime.now(kst)

    print(f"  UTC: {utc_now.strftime('%H:%M')}")
    print(f"  KST: {kst_now.strftime('%H:%M')}")
    print()


def lesson4_json_csv():
    # =========================================================================
    #
    #   레슨 4 — json/csv 다루기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : json/csv 다루기            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ JSON — 데이터 교환의 왕
    # ─────────────────────────────────────────────────────────────────────
    #
    #   JSON = JavaScript Object Notation
    #   웹 API, 설정 파일 등에서 가장 많이 쓰이는 데이터 형식!
    #
    #   비유: 국제 우편에 쓰는 공통 양식! 어떤 나라(언어)에서든
    #         이 양식으로 보내면 읽을 수 있음
    #
    #   C++ : 별도 라이브러리(nlohmann/json 등) 필요
    #   파이썬: import json 한 줄이면 끝!
    #

    # Python 객체 → JSON 문자열 (직렬화: dumps)
    student = {
        "이름": "민수",
        "나이": 12,
        "과목": ["국어", "수학", "영어"],
        "성적": {"국어": 85, "수학": 92},
        "졸업": False,
        "별명": None
    }

    json_str = json.dumps(student, ensure_ascii=False, indent=2)
    print("  JSON 직렬화:")
    print(f"  {json_str[:80]}...")
    print()

    # JSON 문자열 → Python 객체 (역직렬화: loads)
    json_text = '{"name": "Minsu", "score": 95, "passed": true}'
    data = json.loads(json_text)
    print(f"  JSON 역직렬화: {data}")
    print(f"  타입: {type(data)}")  # dict
    print(f"  이름: {data['name']}")
    print()

    # ★ JSON ↔ Python 타입 매핑
    #   JSON     Python
    #   object   dict
    #   array    list
    #   string   str
    #   number   int / float
    #   true     True
    #   false    False
    #   null     None

    # 파일로 저장/읽기
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                     delete=False, encoding='utf-8') as f:
        json.dump(student, f, ensure_ascii=False, indent=2)
        tmp_json = f.name

    with open(tmp_json, 'r', encoding='utf-8') as f:
        loaded = json.load(f)
    print(f"  파일에서 읽기: {loaded['이름']} ({loaded['나이']}살)")
    os.unlink(tmp_json)
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ CSV — 표 형태의 데이터
    # ─────────────────────────────────────────────────────────────────────
    #
    #   CSV = Comma-Separated Values (쉼표로 구분된 값)
    #   엑셀에서 내보내기 하면 CSV!
    #
    #   비유: 줄 노트에 쉼표로 구분해서 적은 표!
    #

    # CSV 쓰기
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                     delete=False, newline='',
                                     encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["이름", "나이", "점수"])    # 헤더
        writer.writerow(["민수", 12, 85])
        writer.writerow(["지유", 13, 95])
        writer.writerow(["서연", 12, 90])
        tmp_csv = f.name

    # CSV 읽기 (일반 reader)
    print("  CSV 읽기 (reader):")
    with open(tmp_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            print(f"    {row}")
    print()

    # CSV 읽기 (DictReader — 딕셔너리로!)
    print("  CSV 읽기 (DictReader):")
    with open(tmp_csv, 'r', encoding='utf-8') as f:
        dict_reader = csv.DictReader(f)
        for row in dict_reader:
            print(f"    {row['이름']}: {row['점수']}점")

    os.unlink(tmp_csv)
    print()


def lesson5_regex():
    # =========================================================================
    #
    #   레슨 5 — re(정규표현식) 기초
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 정규표현식(regex) 기초     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 정규표현식이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   문자열에서 특정 패턴을 찾는 강력한 도구!
    #
    #   비유: "Where's Wally?" 에서 빨간 줄무늬 옷을 입은 사람을
    #         자동으로 찾아주는 로봇!
    #
    #   C++ : <regex> 헤더 (문법은 거의 같음)
    #

    # ─────────────────────────────────────────────────────────────────────
    # ■ 기본 패턴 문법
    # ─────────────────────────────────────────────────────────────────────
    #
    #   .     : 아무 문자 1개 (줄바꿈 제외)
    #   \d    : 숫자 [0-9]
    #   \w    : 단어 문자 [a-zA-Z0-9_]
    #   \s    : 공백 문자 (스페이스, 탭, 줄바꿈)
    #   ^     : 문자열 시작
    #   $     : 문자열 끝
    #   *     : 0번 이상 반복
    #   +     : 1번 이상 반복
    #   ?     : 0번 또는 1번
    #   {n}   : 정확히 n번
    #   {n,m} : n~m번
    #   [abc] : a, b, c 중 하나
    #   (x|y) : x 또는 y
    #

    text = "전화번호는 010-1234-5678이고, 이메일은 test@example.com입니다."

    # ─────────────────────────────────────────────────────────────────────
    # ■ re.search — 패턴 처음 찾기
    # ─────────────────────────────────────────────────────────────────────
    match = re.search(r'\d{3}-\d{4}-\d{4}', text)
    if match:
        print(f"  전화번호 발견: {match.group()}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ re.findall — 모든 매치 찾기
    # ─────────────────────────────────────────────────────────────────────
    numbers = re.findall(r'\d+', text)
    print(f"  모든 숫자: {numbers}")

    # 이메일 찾기
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
    print(f"  이메일: {emails}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ re.match — 문자열 시작부터 매치
    # ─────────────────────────────────────────────────────────────────────
    #
    #   match: 문자열 "처음"부터 매치 시도
    #   search: 문자열 "어디서든" 매치 시도
    #
    result1 = re.match(r'\d+', "123abc")
    result2 = re.match(r'\d+', "abc123")
    print(f"  match('123abc'): {result1.group() if result1 else None}")
    print(f"  match('abc123'): {result2}")  # None (시작이 숫자 아님)
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ re.sub — 패턴 치환
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: "찾기 및 바꾸기" (Ctrl+H)의 강력 버전!
    #
    censored = re.sub(r'\d', '*', text)
    print(f"  숫자 가리기: {censored}")

    # 전화번호 포맷 변환
    phone = "01012345678"
    formatted = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1-\2-\3', phone)
    print(f"  포맷 변환: {formatted}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 그룹 캡처 — 괄호()로 일부만 추출
    # ─────────────────────────────────────────────────────────────────────
    log = "2026-03-21 ERROR 서버 접속 실패"
    m = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\w+)\s+(.*)', log)
    if m:
        print(f"  날짜: {m.group(1)}")
        print(f"  레벨: {m.group(2)}")
        print(f"  메시지: {m.group(3)}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 실전 예제: 데이터 검증
    # ─────────────────────────────────────────────────────────────────────
    def is_valid_email(email):
        pattern = r'^[\w.+-]+@[\w-]+\.[\w.]+$'
        return bool(re.match(pattern, email))

    def is_valid_phone(phone):
        pattern = r'^01[016789]-?\d{3,4}-?\d{4}$'
        return bool(re.match(pattern, phone))

    test_emails = ["test@example.com", "invalid@", "a@b.c", "user@domain.co.kr"]
    for e in test_emails:
        print(f"  '{e}' 유효? {is_valid_email(e)}")

    test_phones = ["010-1234-5678", "01112345678", "02-123-4567"]
    for p in test_phones:
        print(f"  '{p}' 유효? {is_valid_phone(p)}")
    print()


def lesson6_packages():
    # =========================================================================
    #
    #   레슨 6 — 패키지 만들기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 패키지 만들기              │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 패키지란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   패키지 = 모듈을 담은 폴더 (디렉토리)
    #
    #   비유: 모듈 = 도구 하나 (망치)
    #         패키지 = 도구함 (망치, 드라이버, 렌치가 든 상자)
    #
    #   C++ : 네임스페이스와 비슷한 역할
    #

    # ─────────────────────────────────────────────────────────────────────
    # ■ 패키지 구조
    # ─────────────────────────────────────────────────────────────────────
    #
    #   my_package/             ← 패키지 (폴더)
    #   ├── __init__.py         ← "이 폴더는 패키지입니다" 표시
    #   ├── module_a.py         ← 모듈 A
    #   ├── module_b.py         ← 모듈 B
    #   └── sub_package/        ← 하위 패키지
    #       ├── __init__.py
    #       └── module_c.py
    #
    #   ★ __init__.py 파일이 있어야 패키지로 인식! (Python 3.3+에서는 없어도 되긴 함)
    #

    # 실제로 임시 패키지를 만들어 봅시다!
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = Path(tmpdir) / "school"
        pkg_dir.mkdir()

        # __init__.py: 패키지 초기화 파일
        (pkg_dir / "__init__.py").write_text(
            '"""학교 관리 패키지"""\n'
            '__version__ = "1.0.0"\n'
            'from .student import Student\n',  # 상대 임포트!
            encoding="utf-8"
        )

        # student.py 모듈
        (pkg_dir / "student.py").write_text(
            'class Student:\n'
            '    def __init__(self, name):\n'
            '        self.name = name\n'
            '    def greet(self):\n'
            '        return f"안녕! 나는 {self.name}"\n',
            encoding="utf-8"
        )

        # grade.py 모듈
        (pkg_dir / "grade.py").write_text(
            'def calculate_average(scores):\n'
            '    return sum(scores) / len(scores)\n',
            encoding="utf-8"
        )

        # 하위 패키지
        sub_dir = pkg_dir / "utils"
        sub_dir.mkdir()
        (sub_dir / "__init__.py").write_text("", encoding="utf-8")
        (sub_dir / "helpers.py").write_text(
            'def format_score(score):\n'
            '    return f"{score:.1f}점"\n',
            encoding="utf-8"
        )

        # 생성된 구조 확인
        print("  생성된 패키지 구조:")
        for f in sorted(Path(tmpdir).rglob("*")):
            depth = len(f.relative_to(tmpdir).parts) - 1
            indent = "  " * depth
            print(f"    {indent}{f.name}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 상대 임포트 vs 절대 임포트
    # ─────────────────────────────────────────────────────────────────────
    #
    #   절대 임포트: from school.student import Student
    #   상대 임포트: from .student import Student (같은 패키지 안에서)
    #              from ..utils import helpers (상위 패키지에서)
    #
    #   ★ 상대 임포트는 패키지 안에서만 사용 가능!
    #     직접 실행하는 파일에서는 사용 불가!
    #
    print("  절대 임포트: from school.student import Student")
    print("  상대 임포트: from .student import Student")
    print("  ★ 상대 임포트는 패키지 내부에서만!")
    print()


def lesson7_pip_venv():
    # =========================================================================
    #
    #   레슨 7 — pip와 가상환경
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : pip와 가상환경             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ pip — 파이썬 패키지 관리자
    # ─────────────────────────────────────────────────────────────────────
    #
    #   pip = Package Installer for Python
    #   다른 사람이 만든 패키지를 설치하는 도구!
    #
    #   비유: 앱스토어! 필요한 앱(패키지)을 검색하고 설치
    #
    #   C++ : vcpkg, conan 등 (파이썬보다 복잡!)
    #
    #   주요 명령어:
    #   pip install 패키지명          # 설치
    #   pip install 패키지==1.0.0     # 특정 버전 설치
    #   pip uninstall 패키지명        # 삭제
    #   pip list                      # 설치된 패키지 목록
    #   pip show 패키지명             # 패키지 정보
    #   pip freeze                    # 설치된 패키지 + 버전 출력
    #   pip freeze > requirements.txt # 현재 환경 저장!
    #   pip install -r requirements.txt  # 환경 복원!
    #
    print("  ★ pip 주요 명령어:")
    print("    pip install requests       # 설치")
    print("    pip install requests==2.28  # 버전 지정")
    print("    pip list                    # 설치 목록")
    print("    pip freeze > requirements.txt  # 환경 저장")
    print("    pip install -r requirements.txt  # 환경 복원")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 가상환경 (venv) — 프로젝트별 독립 환경
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 각 프로젝트마다 별도의 방을 만드는 것!
    #         A 프로젝트는 requests 2.28, B 프로젝트는 requests 2.31
    #         → 충돌 없이 각자 쓸 수 있음
    #
    #   C++ : 비슷한 개념 없음 (대신 CMake, vcpkg로 관리)
    #
    #   사용법:
    #   1. python -m venv myenv        # 가상환경 생성
    #   2. myenv\Scripts\activate      # 활성화 (Windows)
    #      source myenv/bin/activate   # 활성화 (Mac/Linux)
    #   3. pip install ...             # 패키지 설치 (이 환경에만!)
    #   4. deactivate                  # 비활성화
    #
    print("  ★ 가상환경 사용법:")
    print("    python -m venv myenv        # 생성")
    print("    myenv\\Scripts\\activate      # 활성화 (Windows)")
    print("    source myenv/bin/activate   # 활성화 (Mac/Linux)")
    print("    pip install requests        # 이 환경에만 설치!")
    print("    deactivate                  # 비활성화")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ requirements.txt — 환경 공유의 핵심
    # ─────────────────────────────────────────────────────────────────────
    #
    #   팀원들과 같은 환경을 공유하기 위한 파일!
    #
    #   형식 예시:
    #   requests==2.31.0
    #   numpy>=1.24.0
    #   pandas~=2.0
    #
    #   == : 정확히 이 버전
    #   >= : 이 버전 이상
    #   ~= : 이 버전과 호환 (마이너 업데이트까지 허용)
    #
    print("  ★ requirements.txt 버전 표기법:")
    print("    requests==2.31.0    # 정확히 이 버전")
    print("    numpy>=1.24.0       # 이 버전 이상")
    print("    pandas~=2.0         # 호환 버전 (2.0.x)")
    print()


def lesson8_builtin_functions():
    # =========================================================================
    #
    #   레슨 8 — 유용한 내장 함수 총정리
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 유용한 내장 함수 총정리    │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ enumerate — 인덱스와 값을 함께!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 줄 서 있는 사람들에게 번호표 나눠주기!
    #
    #   C++ : for(int i=0; i<v.size(); i++) { ... v[i] ... }
    #   파이썬: for i, v in enumerate(list): ...
    #
    fruits = ["사과", "바나나", "체리"]
    print("  enumerate:")
    for i, fruit in enumerate(fruits):
        print(f"    {i}: {fruit}")

    # start 파라미터로 시작 번호 변경!
    print("  enumerate(start=1):")
    for i, fruit in enumerate(fruits, start=1):
        print(f"    {i}번째: {fruit}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ zip — 여러 리스트를 나란히 묶기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 지퍼! 두 줄을 하나로 엮기
    #
    names = ["민수", "지유", "서연"]
    scores = [85, 95, 90]
    grades = ["B", "A", "A"]

    print("  zip (2개):")
    for name, score in zip(names, scores):
        print(f"    {name}: {score}점")

    print("  zip (3개):")
    for name, score, grade in zip(names, scores, grades):
        print(f"    {name}: {score}점 ({grade})")

    # ★ 길이가 다르면? 짧은 쪽에 맞춤!
    short = [1, 2]
    long = [10, 20, 30, 40]
    print(f"  zip 길이 다를 때: {list(zip(short, long))}")  # [(1,10), (2,20)]
    print()

    # zip으로 딕셔너리 만들기!
    student_dict = dict(zip(names, scores))
    print(f"  zip → dict: {student_dict}")

    # unzip (별표로 풀기!)
    pairs = [(1, "a"), (2, "b"), (3, "c")]
    nums, chars = zip(*pairs)
    print(f"  unzip: 숫자={nums}, 문자={chars}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ map — 모든 원소에 함수 적용
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 컨베이어 벨트! 각 물건에 같은 처리를 적용
    #
    numbers = [1, 2, 3, 4, 5]
    squared = list(map(lambda x: x**2, numbers))
    print(f"  map (제곱): {squared}")

    # 문자열 → 정수 변환에 자주 사용!
    str_nums = ["10", "20", "30"]
    int_nums = list(map(int, str_nums))
    print(f"  map (문자→숫자): {int_nums}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ filter — 조건에 맞는 것만 걸러내기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 체! 조건에 맞는 것만 통과
    #
    all_numbers = range(1, 21)
    evens = list(filter(lambda x: x % 2 == 0, all_numbers))
    print(f"  filter (짝수): {evens}")

    # None을 넣으면 truthy한 값만 남김
    mixed = [0, 1, "", "hello", None, True, False, [], [1]]
    truthy = list(filter(None, mixed))
    print(f"  filter(None): {truthy}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ sorted — 정렬 (원본 변경 없음!)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   key 파라미터로 정렬 기준을 지정!
    #
    words = ["banana", "apple", "cherry", "date"]
    print(f"  기본 정렬: {sorted(words)}")
    print(f"  길이 정렬: {sorted(words, key=len)}")
    print(f"  역순 정렬: {sorted(words, reverse=True)}")

    # 딕셔너리 정렬
    students_data = {"민수": 85, "지유": 95, "서연": 90}
    by_score = sorted(students_data.items(), key=lambda x: x[1], reverse=True)
    print(f"  점수순 정렬: {by_score}")

    # 복합 키 정렬
    people = [("민수", 12), ("지유", 13), ("서연", 12), ("하준", 13)]
    by_age_name = sorted(people, key=lambda x: (x[1], x[0]))
    print(f"  나이→이름순: {by_age_name}")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ any, all — 조건 검사
    # ─────────────────────────────────────────────────────────────────────
    #
    #   any(): 하나라도 True면 True (OR의 리스트 버전)
    #   all(): 전부 True여야 True (AND의 리스트 버전)
    #
    #   비유: any = "한 명이라도 손 들었나?"
    #         all = "전원 다 손 들었나?"
    #
    scores_list = [85, 92, 78, 95, 88]
    print(f"  any(>90): {any(s > 90 for s in scores_list)}")    # True
    print(f"  all(>70): {all(s > 70 for s in scores_list)}")    # True
    print(f"  all(>80): {all(s > 80 for s in scores_list)}")    # False
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ isinstance, type — 타입 확인
    # ─────────────────────────────────────────────────────────────────────
    x = 42
    print(f"  type(42): {type(x)}")
    print(f"  isinstance(42, int): {isinstance(x, int)}")
    print(f"  isinstance(42, (int, float)): {isinstance(x, (int, float))}")
    # ★ isinstance는 상속도 체크! type은 정확한 타입만 체크!
    print(f"  isinstance(True, int): {isinstance(True, int)}")   # True! (bool은 int의 자식)
    print(f"  type(True) == int: {type(True) == int}")           # False!
    print()


def main():
    print("■■■ Python 학습 06단계: 모듈과 패키지 완전정복 ■■■")
    print()
    lesson1_import()
    lesson2_stdlib_files()
    lesson3_datetime()
    lesson4_json_csv()
    lesson5_regex()
    lesson6_packages()
    lesson7_pip_venv()
    lesson8_builtin_functions()


if __name__ == "__main__":
    main()
