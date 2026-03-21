# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 07단계: 파일 입출력과 예외 처리
#   ─ 파일 읽기/쓰기, 경로, CSV/JSON, 예외, 커스텀 예외, 베스트 프랙티스 ─
#
#   파일은 "컴퓨터 속 공책"이고, 예외 처리는 "실수 대비 안전벨트"입니다.
#   프로그램이 데이터를 저장하고, 불러오고, 에러 상황에서도 무너지지 않게
#   만드는 모든 기술을 이 파일 하나로 배웁니다.
#
#   ■ 실행 방법: python 07_files_exceptions.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 파일 열기/닫기 기초 - open(), close(), with문
#   2. 텍스트 파일 읽기 - read(), readline(), readlines(), 인코딩
#   3. 텍스트 파일 쓰기 - write(), writelines(), 'w' vs 'a' 모드
#   4. 파일 경로 다루기 - os.path vs pathlib, Path 객체
#   5. CSV/JSON 파일 - csv.reader/writer, json.dump/load
#   6. 예외(Exception) 기초 - try/except/else/finally
#   7. 예외 종류 총정리 - ValueError, TypeError 등 하나하나 예제
#   8. 커스텀 예외 만들기 - 상속, raise, 실전 패턴
#   9. 예외 처리 베스트 프랙티스 - EAFP vs LBYL, 로깅
#  10. 실전: 학생 성적 파일 관리 시스템
#
# ─────────────────────────────────────────────────────────────────────────

import os
import csv
import json
import tempfile
from pathlib import Path


def lesson1_file_open_close():
    # =========================================================================
    #
    #   레슨 1 — 파일 열기/닫기 기초: open(), close(), with문
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 파일 열기/닫기 기초        │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 파일이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   파일 = 컴퓨터의 하드디스크에 저장된 데이터 묶음
    #
    #   비유: 파일은 "공책"입니다.
    #         - 공책을 "열어야(open)" 글을 쓰거나 읽을 수 있음
    #         - 다 쓰면 "닫아야(close)" 다른 사람도 쓸 수 있음
    #         - 닫지 않으면? 다른 프로그램이 못 쓰거나, 데이터가 날아갈 수 있음!
    #
    #   파일 모드:
    #     'r'  = read   → 읽기 전용 (기본값)
    #     'w'  = write  → 쓰기 (기존 내용 삭제!)
    #     'a'  = append → 추가 (기존 내용 뒤에 이어서)
    #     'x'  = create → 새 파일 생성 (이미 있으면 에러!)
    #     'b'  = binary → 바이너리 모드 (이미지, 동영상 등)
    #     'rb', 'wb' 처럼 조합 가능
    #

    with tempfile.TemporaryDirectory() as tmp:
        filepath = os.path.join(tmp, "test.txt")

        # ── 방법 1: open()과 close() 직접 사용 (옛날 방식, 비추천) ──
        #
        # 문제점: close()를 깜빡하면 데이터 손실 가능!
        #         에러가 나면 close()에 도달하지 못할 수도 있음
        #
        f = open(filepath, 'w', encoding='utf-8')
        f.write("안녕하세요\n")
        f.close()  # ← 반드시 닫아야 함!
        print("  방법 1 (open/close): 파일 작성 완료")

        # ── 방법 2: with문 사용 (컨텍스트 매니저, 강력 추천!) ──
        #
        # with문 = "자동 문 닫기 장치"
        # 비유: 호텔 방문을 열면 자동으로 닫히는 도어클로저와 같음
        #       with 블록을 벗어나면 자동으로 file.close() 호출!
        #       심지어 에러가 발생해도 자동으로 닫아줌!
        #
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("with문으로 작성한 내용\n")
            f.write("자동으로 닫힘!\n")
        # ← 여기서 자동으로 f.close() 실행됨

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  방법 2 (with문): {content.strip()}")

        # ── with문이 왜 중요한가? ──
        #
        #   나쁜 예:
        #     f = open("data.txt")
        #     data = f.read()
        #     process(data)         # ← 여기서 에러 나면?
        #     f.close()             # ← 이 줄 실행 안 됨! 파일 안 닫힘!
        #
        #   좋은 예:
        #     with open("data.txt") as f:
        #         data = f.read()
        #         process(data)     # ← 에러 나도 파일은 자동으로 닫힘!
        #

        # ── 파일 객체의 속성들 ──
        with open(filepath, 'r', encoding='utf-8') as f:
            print(f"  f.name    = {f.name}")       # 파일 이름
            print(f"  f.mode    = {f.mode}")       # 모드 ('r', 'w', 등)
            print(f"  f.closed  = {f.closed}")     # 닫혔는지 여부
        print(f"  f.closed (with 밖) = {f.closed}")  # with 밖에서는 True!
    print()


def lesson2_read_text_file():
    # =========================================================================
    #
    #   레슨 2 — 텍스트 파일 읽기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 텍스트 파일 읽기           │")
    print("└──────────────────────────────────────┘")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        filepath = os.path.join(tmp, "poem.txt")

        # 먼저 테스트용 파일 만들기
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("봄이 오면\n")
            f.write("산에 들에 진달래 피네\n")
            f.write("진달래 피네\n")
            f.write("갈 봄 여름 없이\n")
            f.write("피는 산 진달래야\n")

        # ── 방법 1: read() — 파일 전체를 하나의 문자열로 ──
        #
        # 비유: 공책 전체를 한 번에 복사기에 넣는 것
        # 주의: 파일이 크면 메모리를 많이 잡아먹음!
        #       1GB 파일을 read()하면 1GB 메모리 사용!
        #
        with open(filepath, 'r', encoding='utf-8') as f:
            all_text = f.read()
        print("  [read()] 전체 읽기:")
        print(f"  {repr(all_text[:30])}...")  # repr로 \n 보이게

        # ── 방법 2: readline() — 한 줄씩 읽기 ──
        #
        # 비유: 공책 한 줄 읽고, 또 한 줄 읽고...
        # 특징: 줄 끝에 \n이 포함됨!
        #
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline()     # "봄이 오면\n"
            second_line = f.readline()    # "산에 들에...\n"
        print(f"  [readline()] 첫 줄: {first_line.strip()}")
        print(f"  [readline()] 둘째 줄: {second_line.strip()}")

        # ── 방법 3: readlines() — 모든 줄을 리스트로 ──
        #
        # 비유: 공책을 줄 단위로 찢어서 리스트에 넣기
        # 각 요소 끝에 \n이 포함됨!
        #
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"  [readlines()] 줄 수: {len(lines)}개")
        print(f"  [readlines()] 첫 줄: {repr(lines[0])}")  # '\n' 포함!

        # ── 방법 4: for line in file — 가장 추천하는 방법! ──
        #
        # 비유: 공책을 한 줄씩 넘기면서 읽기
        # 장점: 메모리를 적게 씀! (한 줄만 메모리에 있으니까)
        #       10GB 파일도 문제 없음!
        #
        print("  [for문] 한 줄씩 읽기:")
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                print(f"    {i}: {line.strip()}")

        # ── 인코딩(encoding) 이야기 ──
        #
        # 인코딩 = "글자를 숫자로 바꾸는 규칙"
        #
        #   UTF-8  : 전 세계 모든 언어 지원 (표준! 항상 이걸 쓰자)
        #   cp949  : 옛날 윈도우 한글 인코딩 (가끔 만남)
        #   euc-kr : 더 옛날 한글 인코딩
        #
        #   ★ 꿀팁: 파일 읽을 때 UnicodeDecodeError가 나면?
        #     → encoding='cp949' 또는 encoding='euc-kr' 시도!
        #     → 또는 errors='ignore' 로 깨진 글자 무시 가능
        #
        #   with open("old_file.txt", 'r', encoding='cp949') as f:
        #       text = f.read()
        #
        #   with open("messy.txt", 'r', encoding='utf-8', errors='ignore') as f:
        #       text = f.read()   # 깨진 글자는 건너뜀
        #

        # ── read(N) — N글자만 읽기 ──
        with open(filepath, 'r', encoding='utf-8') as f:
            chunk = f.read(5)    # 5글자만 읽기
            print(f"  [read(5)] 5글자만: '{chunk}'")
            rest = f.read()      # 나머지 전부 읽기
            print(f"  [read()] 나머지 글자 수: {len(rest)}")
    print()


def lesson3_write_text_file():
    # =========================================================================
    #
    #   레슨 3 — 텍스트 파일 쓰기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 텍스트 파일 쓰기           │")
    print("└──────────────────────────────────────┘")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        filepath = os.path.join(tmp, "diary.txt")

        # ── write() — 문자열 하나를 파일에 쓰기 ──
        #
        # 주의: write()는 자동으로 줄바꿈을 안 함!
        #       \n을 직접 넣어야 줄이 바뀜!
        #       (print()와 다름! print는 자동 줄바꿈)
        #
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("2024년 3월 1일\n")
            f.write("오늘 파이썬 공부를 시작했다.\n")
            f.write("생각보다 재밌다!\n")

        with open(filepath, 'r', encoding='utf-8') as f:
            print("  [write()] 결과:")
            print(f"  {f.read().strip()}")

        # ── writelines() — 리스트를 한번에 쓰기 ──
        #
        # 주의: writelines()도 자동 줄바꿈 안 함!
        #       각 요소 끝에 \n을 직접 넣어야 함!
        #
        lines = ["첫째 줄\n", "둘째 줄\n", "셋째 줄\n"]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print()

        with open(filepath, 'r', encoding='utf-8') as f:
            print(f"  [writelines()] 결과: {f.read().strip()}")

        # ── 'w' vs 'a' 모드의 차이 ──
        #
        # 'w' (write)  = 기존 내용 전부 삭제하고 새로 쓰기
        #                비유: 공책을 찢어버리고 새 공책에 쓰기
        #
        # 'a' (append) = 기존 내용 뒤에 이어서 쓰기
        #                비유: 공책 마지막 페이지 이후에 이어서 쓰기
        #
        # ★ 실수 주의!
        #   'w' 모드로 열면 기존 내용이 모두 사라짐!
        #   중요한 데이터를 'w'로 열었다가 날릴 수 있음!
        #
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("원래 내용\n")

        with open(filepath, 'a', encoding='utf-8') as f:  # 'a' = 추가!
            f.write("추가된 내용\n")

        with open(filepath, 'r', encoding='utf-8') as f:
            print(f"\n  ['a' 모드] 결과:\n  {f.read().strip()}")

        # ── print()로 파일에 쓰기 (file= 매개변수) ──
        #
        # print()의 출력 대상을 파일로 바꿀 수 있음!
        # 장점: 자동 줄바꿈, 여러 값을 쉽게 출력
        #
        with open(filepath, 'w', encoding='utf-8') as f:
            print("이름: 홍길동", file=f)
            print("나이:", 25, file=f)
            print(f"점수: {95}점", file=f)

        with open(filepath, 'r', encoding='utf-8') as f:
            print(f"\n  [print(file=f)] 결과:\n  {f.read().strip()}")
    print()


def lesson4_file_paths():
    # =========================================================================
    #
    #   레슨 4 — 파일 경로 다루기: os.path vs pathlib
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 파일 경로 다루기           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 경로(Path)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   경로 = 파일이 어디 있는지 알려주는 주소
    #
    #   윈도우: C:\Users\student\Desktop\homework.txt  (역슬래시 \)
    #   맥/리눅스: /home/student/Desktop/homework.txt  (슬래시 /)
    #
    #   절대경로: 컴퓨터 루트부터 전체 주소  ("/home/user/file.txt")
    #   상대경로: 현재 위치 기준 주소  ("./data/file.txt")
    #

    # ── 옛날 방식: os.path (문자열 기반) ──
    #
    # 동작은 하지만, 문자열 조작이라 실수하기 쉬움
    #
    print("  [os.path 방식]")
    print(f"  현재 디렉토리: {os.getcwd()}")
    joined = os.path.join("data", "scores", "2024.csv")
    print(f"  os.path.join: {joined}")
    print(f"  파일명만: {os.path.basename(joined)}")
    print(f"  폴더만: {os.path.dirname(joined)}")
    print(f"  확장자: {os.path.splitext(joined)}")

    # ── 새 방식: pathlib.Path (객체 기반, 추천!) ──
    #
    # Path 객체 = "똑똑한 경로"
    # 비유: 문자열 경로가 "종이에 적힌 주소"라면,
    #       Path 객체는 "네비게이션"입니다!
    #       경로 조합, 파일 존재 확인, 읽기/쓰기 등 다 가능
    #
    print("\n  [pathlib.Path 방식]")
    p = Path("data") / "scores" / "2024.csv"     # / 연산자로 경로 조합!
    print(f"  Path 조합: {p}")
    print(f"  파일명: {p.name}")          # "2024.csv"
    print(f"  확장자: {p.suffix}")        # ".csv"
    print(f"  확장자 없는 이름: {p.stem}")  # "2024"
    print(f"  부모 폴더: {p.parent}")     # "data/scores"

    # ── Path 객체의 유용한 메서드들 ──
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_file = tmp_path / "hello.txt"
        test_dir = tmp_path / "subdir"

        # 파일 존재 여부 확인
        print(f"\n  파일 존재? {test_file.exists()}")          # False

        # 파일 생성
        test_file.write_text("안녕!", encoding='utf-8')
        print(f"  파일 존재? {test_file.exists()}")            # True
        print(f"  파일인가? {test_file.is_file()}")            # True
        print(f"  폴더인가? {test_file.is_dir()}")             # False

        # 디렉토리 생성
        test_dir.mkdir(parents=True, exist_ok=True)
        print(f"  폴더 존재? {test_dir.is_dir()}")             # True

        # ── glob: 파일 패턴 검색 ──
        #
        # glob = "이 패턴에 맞는 파일 다 찾아줘"
        # * = 아무 글자, ** = 하위 폴더 포함
        #
        (tmp_path / "a.txt").write_text("a", encoding='utf-8')
        (tmp_path / "b.txt").write_text("b", encoding='utf-8')
        (tmp_path / "c.py").write_text("c", encoding='utf-8')

        txt_files = list(tmp_path.glob("*.txt"))
        print(f"\n  .txt 파일들: {[f.name for f in txt_files]}")

        all_files = list(tmp_path.glob("**/*"))
        print(f"  모든 파일: {[f.name for f in all_files if f.is_file()]}")
    print()


def lesson5_csv_json():
    # =========================================================================
    #
    #   레슨 5 — CSV/JSON 파일 다루기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : CSV/JSON 파일 처리         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ CSV란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   CSV = Comma Separated Values (쉼표로 구분된 값)
    #
    #   비유: 엑셀 표를 텍스트로 저장한 것
    #
    #   이름,국어,수학
    #   민수,95,88
    #   지유,100,97
    #
    #   ★ 주의: 값 안에 쉼표가 있으면? → "서울시, 강남구" 처럼 따옴표로 감싸기
    #

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "scores.csv")

        # ── CSV 쓰기 ──
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["이름", "국어", "수학"])       # 헤더
            writer.writerow(["민수", 95, 88])
            writer.writerow(["지유", 100, 97])
            writer.writerow(["서연", 88, 92])
        print("  CSV 파일 작성 완료!")

        # ── CSV 읽기 ──
        print("  CSV 읽기:")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)   # 첫 줄 = 헤더
            print(f"    헤더: {header}")
            for row in reader:
                name, kor, math = row[0], int(row[1]), int(row[2])
                print(f"    {name}: 국어={kor}, 수학={math}, 합계={kor+math}")

        # ── DictReader/DictWriter — 더 편한 방법! ──
        #
        # DictReader: 각 행을 딕셔너리로 읽기 {"이름": "민수", "국어": "95", ...}
        # DictWriter: 딕셔너리를 행으로 쓰기
        #
        print("\n  DictReader로 읽기:")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"    {row['이름']}: 국어={row['국어']}, 수학={row['수학']}")

        # ─────────────────────────────────────────────────────────────────
        # ■ JSON이란?
        # ─────────────────────────────────────────────────────────────────
        #
        #   JSON = JavaScript Object Notation
        #
        #   비유: 파이썬의 딕셔너리/리스트를 텍스트로 저장하는 국제 표준 형식
        #
        #   { "name": "민수", "scores": [95, 88] }
        #
        #   ★ 파이썬 ↔ JSON 타입 대응:
        #     dict  ↔ object {}
        #     list  ↔ array []
        #     str   ↔ string ""
        #     int   ↔ number
        #     float ↔ number
        #     True  ↔ true     (대소문자 주의!)
        #     False ↔ false
        #     None  ↔ null
        #

        json_path = os.path.join(tmp, "students.json")

        students = [
            {"이름": "민수", "나이": 16, "과목": {"국어": 95, "수학": 88}},
            {"이름": "지유", "나이": 17, "과목": {"국어": 100, "수학": 97}},
            {"이름": "서연", "나이": 16, "과목": {"국어": 88, "수학": 92}},
        ]

        # ── JSON 쓰기 (json.dump) ──
        #
        # ensure_ascii=False → 한글을 \uXXXX 대신 그대로 저장
        # indent=2 → 보기 좋게 들여쓰기
        #
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(students, f, ensure_ascii=False, indent=2)
        print("\n  JSON 파일 작성 완료!")

        # ── JSON 읽기 (json.load) ──
        with open(json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        print("  JSON 읽기:")
        for s in loaded:
            total = sum(s["과목"].values())
            print(f"    {s['이름']} (나이 {s['나이']}): 총점 {total}")

        # ── json.dumps / json.loads — 문자열 ↔ 파이썬 객체 ──
        #
        # dump/load  = 파일에 쓰기/읽기 (File)
        # dumps/loads = 문자열로 변환/파싱 (String) ← 's'가 string!
        #
        json_str = json.dumps({"이름": "테스트"}, ensure_ascii=False)
        print(f"\n  json.dumps: {json_str}")
        parsed = json.loads(json_str)
        print(f"  json.loads: {parsed}")
    print()


def lesson6_exception_basics():
    # =========================================================================
    #
    #   레슨 6 — 예외(Exception) 기초
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 예외(Exception) 기초       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 예외(Exception)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   예외 = 프로그램 실행 중에 발생하는 에러
    #
    #   비유: "갑자기 빗길에서 차가 미끄러지는 것"
    #         안전벨트(try/except)가 없으면 프로그램이 죽음!
    #         안전벨트가 있으면 멈추지 않고 대처할 수 있음!
    #
    #   예외가 없으면? → 프로그램이 즉시 멈추고 에러 메시지 출력
    #   예외 처리하면? → 에러를 잡아서 우아하게 대처 가능
    #

    # ── try / except 기본 구조 ──
    #
    #   try:
    #       위험한 코드 (에러가 날 수 있는 코드)
    #   except 에러종류:
    #       에러가 났을 때 실행할 코드
    #
    print("  [기본 try/except]")
    try:
        result = 10 / 0    # ZeroDivisionError 발생!
    except ZeroDivisionError:
        print("  0으로 나눌 수 없습니다!")

    # ── except에 에러 객체 받기 (as e) ──
    try:
        number = int("abc")
    except ValueError as e:
        print(f"  숫자 변환 실패: {e}")

    # ── try / except / else / finally 완전 구조 ──
    #
    #   try:
    #       위험한 코드
    #   except 에러종류:
    #       에러 발생 시 실행
    #   else:
    #       에러가 안 났을 때만 실행 (성공했을 때!)
    #   finally:
    #       에러가 나든 안 나든 항상 실행 (정리 작업!)
    #
    #   비유:
    #     try     = 요리 시도
    #     except  = 요리 실패 → "배달 시켜!"
    #     else    = 요리 성공 → "맛있게 먹자!"
    #     finally = 무조건 → "설거지!" (성공이든 실패든)
    #
    print("\n  [try/except/else/finally]")

    def divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            print(f"    에러: {a}/{b} → 0으로 나눌 수 없음!")
            return None
        except TypeError:
            print(f"    에러: {a}/{b} → 타입이 맞지 않음!")
            return None
        else:
            # 에러가 안 났을 때만 실행!
            print(f"    성공: {a}/{b} = {result}")
            return result
        finally:
            # 항상 실행!
            print(f"    정리: divide({a}, {b}) 함수 종료")

    divide(10, 3)
    divide(10, 0)
    divide("10", [])

    # ── 여러 예외를 한번에 잡기 ──
    print("\n  [여러 예외 잡기]")
    try:
        data = [1, 2, 3]
        print(data[10])
    except (IndexError, KeyError) as e:
        print(f"  인덱스/키 에러: {type(e).__name__}: {e}")
    print()


def lesson7_exception_types():
    # =========================================================================
    #
    #   레슨 7 — 예외 종류 총정리
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 예외 종류 총정리           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 파이썬 주요 예외 한눈에 보기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   BaseException
    #   ├── SystemExit          (sys.exit() 호출)
    #   ├── KeyboardInterrupt   (Ctrl+C 누름)
    #   └── Exception           (일반 예외의 부모)
    #       ├── ValueError      (값이 이상함)
    #       ├── TypeError       (타입이 안 맞음)
    #       ├── KeyError        (딕셔너리 키 없음)
    #       ├── IndexError      (인덱스 초과)
    #       ├── FileNotFoundError (파일 없음)
    #       ├── ZeroDivisionError (0으로 나눔)
    #       ├── AttributeError  (속성/메서드 없음)
    #       ├── NameError       (변수명 없음)
    #       ├── ImportError      (모듈 임포트 실패)
    #       └── ... 그 외 많음
    #

    # ── 1. ValueError: 값이 이상할 때 ──
    print("  [ValueError] - 값의 형식이 맞지 않을 때")
    try:
        int("hello")    # 숫자가 아닌 문자열 → 변환 불가!
    except ValueError as e:
        print(f"    int('hello') → {e}")

    try:
        int("12.5")     # 소수점 문자열 → int() 불가! (float()로 먼저!)
    except ValueError as e:
        print(f"    int('12.5') → {e}")

    # ── 2. TypeError: 타입이 안 맞을 때 ──
    print("\n  [TypeError] - 타입끼리 연산이 안 될 때")
    try:
        result = "나이: " + 25   # 문자열 + 숫자 → 불가!
    except TypeError as e:
        print(f"    '나이: ' + 25 → {e}")

    try:
        len(42)   # 숫자에는 길이가 없음!
    except TypeError as e:
        print(f"    len(42) → {e}")

    # ── 3. KeyError: 딕셔너리에 키가 없을 때 ──
    print("\n  [KeyError] - 딕셔너리에 없는 키를 찾을 때")
    student = {"이름": "민수", "나이": 16}
    try:
        print(student["점수"])   # "점수" 키 없음!
    except KeyError as e:
        print(f"    student['점수'] → KeyError: {e}")
    # ★ 해결법: .get() 사용!
    print(f"    student.get('점수', '없음') → {student.get('점수', '없음')}")

    # ── 4. IndexError: 인덱스 초과 ──
    print("\n  [IndexError] - 리스트 범위를 벗어날 때")
    fruits = ["사과", "바나나", "포도"]
    try:
        print(fruits[10])
    except IndexError as e:
        print(f"    fruits[10] → {e}")

    # ── 5. FileNotFoundError: 파일이 없을 때 ──
    print("\n  [FileNotFoundError] - 존재하지 않는 파일을 열 때")
    try:
        with open("이런_파일_절대_없음.txt", 'r') as f:
            f.read()
    except FileNotFoundError as e:
        print(f"    → {e}")

    # ── 6. ZeroDivisionError: 0으로 나눌 때 ──
    print("\n  [ZeroDivisionError] - 0으로 나눌 때")
    try:
        result = 100 / 0
    except ZeroDivisionError as e:
        print(f"    100 / 0 → {e}")
    try:
        result = 100 % 0    # 나머지 연산도!
    except ZeroDivisionError as e:
        print(f"    100 % 0 → {e}")

    # ── 7. AttributeError: 없는 속성/메서드 호출 ──
    print("\n  [AttributeError] - 없는 속성이나 메서드를 호출할 때")
    try:
        number = 42
        number.append(1)   # 숫자에 append 없음!
    except AttributeError as e:
        print(f"    (42).append(1) → {e}")

    # ── 8. NameError: 정의 안 된 변수 ──
    print("\n  [NameError] - 정의되지 않은 변수를 사용할 때")
    try:
        print(undefined_variable_xyz)
    except NameError as e:
        print(f"    undefined_variable_xyz → {e}")

    # ── 9. StopIteration: 이터레이터 소진 ──
    print("\n  [StopIteration] - 이터레이터가 더 이상 값이 없을 때")
    it = iter([1])
    next(it)     # 1
    try:
        next(it)  # 더 이상 없음!
    except StopIteration:
        print("    next() → 더 이상 값이 없습니다")

    # ── 10. OverflowError: 숫자가 너무 클 때 ──
    print("\n  [OverflowError] - 계산 결과가 너무 클 때")
    try:
        import math
        math.exp(1000)  # e^1000 → 너무 큼!
    except OverflowError as e:
        print(f"    math.exp(1000) → {e}")
    print()


def lesson8_custom_exceptions():
    # =========================================================================
    #
    #   레슨 8 — 커스텀 예외 만들기
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 커스텀 예외 만들기         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 커스텀 예외를 만들까?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   내장 예외만으로는 "우리 프로그램만의 에러"를 표현하기 어려움
    #
    #   예: 은행 프로그램에서 "잔액 부족" → ValueError? 너무 일반적!
    #       → InsufficientBalanceError 라는 전용 예외를 만들면?
    #       → 코드 읽기가 훨씬 명확해짐!
    #
    #   규칙:
    #     1. Exception 클래스를 상속
    #     2. 이름은 ~Error로 끝내기 (관례)
    #     3. 필요하면 추가 정보를 속성으로 저장
    #

    # ── 가장 간단한 커스텀 예외 ──
    class ScoreTooHighError(Exception):
        """점수가 100점을 초과할 때 발생하는 예외"""
        pass     # pass만 해도 됨! Exception의 기능을 그대로 상속

    # ── 추가 정보를 가진 커스텀 예외 ──
    class InvalidScoreError(Exception):
        """유효하지 않은 점수일 때 발생하는 예외"""
        def __init__(self, score, message=None):
            self.score = score
            self.message = message or f"유효하지 않은 점수: {score}"
            super().__init__(self.message)

    # ── raise로 예외 발생시키기 ──
    #
    # raise = "이 에러를 일부러 발생시켜!"
    #
    # 비유: 축구에서 심판이 레드카드를 드는 것
    #       규칙을 어기면 직접 경고를 날림!
    #
    def set_score(name, score):
        if not isinstance(score, (int, float)):
            raise TypeError(f"점수는 숫자여야 합니다. 받은 값: {type(score)}")
        if score < 0:
            raise InvalidScoreError(score, f"점수는 0 이상이어야 합니다: {score}")
        if score > 100:
            raise ScoreTooHighError(f"{name}의 점수가 100을 초과: {score}")
        print(f"    {name}: {score}점 설정 완료!")

    # ── 커스텀 예외 사용하기 ──
    print("  [커스텀 예외 테스트]")
    test_cases = [
        ("민수", 95),
        ("지유", 150),
        ("서연", -10),
        ("하준", "구십"),
    ]

    for name, score in test_cases:
        try:
            set_score(name, score)
        except ScoreTooHighError as e:
            print(f"    {name}: 점수 초과 에러 → {e}")
        except InvalidScoreError as e:
            print(f"    {name}: 유효하지 않은 점수 → {e} (입력값: {e.score})")
        except TypeError as e:
            print(f"    {name}: 타입 에러 → {e}")

    # ── 예외 계층 구조 만들기 (실전 패턴) ──
    #
    # 큰 프로젝트에서는 예외를 계층으로 만듦
    # → except AppError로 앱 전체 에러를 한번에 잡을 수 있음!
    #
    class AppError(Exception):
        """앱의 모든 커스텀 예외의 부모"""
        pass

    class DatabaseError(AppError):
        """데이터베이스 관련 에러"""
        pass

    class NetworkError(AppError):
        """네트워크 관련 에러"""
        pass

    print("\n  [예외 계층 구조]")
    errors = [DatabaseError("DB 연결 실패"), NetworkError("타임아웃")]
    for err in errors:
        try:
            raise err
        except AppError as e:    # 부모 클래스로 한번에 잡기!
            print(f"    앱 에러 발생: {type(e).__name__}: {e}")

    # ── raise from: 예외 체이닝 ──
    #
    # 원래 에러를 보존하면서 새 에러를 발생시킬 때 사용
    #
    print("\n  [raise from - 예외 체이닝]")
    try:
        try:
            int("abc")
        except ValueError as original:
            raise InvalidScoreError("abc", "점수 변환 실패") from original
    except InvalidScoreError as e:
        print(f"    체이닝 에러: {e}")
        print(f"    원래 원인: {e.__cause__}")
    print()


def lesson9_best_practices():
    # =========================================================================
    #
    #   레슨 9 — 예외 처리 베스트 프랙티스
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 예외 처리 베스트 프랙티스  │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 규칙 1: bare except 절대 금지!
    # ─────────────────────────────────────────────────────────────────────
    #
    #   나쁜 예:
    #     try:
    #         something()
    #     except:           # ← bare except! 모든 에러를 삼킴!
    #         pass           # ← 에러를 무시! 디버깅 불가능!
    #
    #   왜 나쁜가?
    #     - KeyboardInterrupt(Ctrl+C)도 잡아버림 → 프로그램 종료 불가!
    #     - 어떤 에러인지 모름 → 디버깅 지옥!
    #     - 버그가 숨어버림!
    #
    #   좋은 예:
    #     try:
    #         something()
    #     except ValueError as e:    # ← 구체적 예외만 잡기!
    #         logging.error(f"값 에러: {e}")
    #

    print("  ★ 규칙 1: bare except (맨 except:) 절대 금지!")
    print("    → 항상 구체적인 예외 타입을 지정하세요")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 규칙 2: 예외를 삼키지 말기! (pass 금지)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   나쁜 예:
    #     except ValueError:
    #         pass    # 에러가 나도 아무것도 안 함 → 문제 숨김!
    #
    #   좋은 예:
    #     except ValueError as e:
    #         print(f"경고: {e}")      # 최소한 로그라도!
    #         # 또는 logging.warning(str(e))
    #

    print("  ★ 규칙 2: except 안에서 pass 쓰지 말기!")
    print("    → 최소한 로그를 남기세요")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 규칙 3: EAFP vs LBYL
    # ─────────────────────────────────────────────────────────────────────
    #
    #   LBYL = Look Before You Leap (뛰기 전에 살펴보기)
    #     → if문으로 미리 확인 후 실행
    #
    #   EAFP = Easier to Ask Forgiveness than Permission
    #          (허락보다 용서가 쉽다)
    #     → 일단 실행하고, 에러나면 그때 처리
    #
    #   ★ 파이썬에서는 EAFP를 선호! (더 파이썬스러운 방식)
    #

    student = {"이름": "민수", "나이": 16}

    # LBYL 방식 (미리 확인)
    print("\n  [LBYL - 미리 확인하기]")
    if "점수" in student:
        print(f"    점수: {student['점수']}")
    else:
        print("    점수 키가 없습니다")

    # EAFP 방식 (일단 실행) — 파이썬스러운 방식!
    print("  [EAFP - 일단 실행하기] ← 파이썬 추천!")
    try:
        print(f"    점수: {student['점수']}")
    except KeyError:
        print("    점수 키가 없습니다")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 규칙 4: 좁은 범위의 try 블록
    # ─────────────────────────────────────────────────────────────────────
    #
    #   나쁜 예:
    #     try:
    #         data = read_file()         # 이것도 try 안?
    #         processed = process(data)   # 이것도?
    #         save(processed)             # 이것도??
    #     except Exception:
    #         print("뭔가 에러!")    # 어디서 에러난지 모름!
    #
    #   좋은 예:
    #     try:
    #         data = read_file()
    #     except FileNotFoundError:
    #         print("파일 없음!")
    #
    #     try:
    #         processed = process(data)
    #     except ValueError:
    #         print("데이터 형식 에러!")
    #

    print("\n  ★ 규칙 4: try 블록은 가능한 좁게!")
    print("    → 어디서 에러 났는지 명확하게")

    # ─────────────────────────────────────────────────────────────────────
    # ■ 규칙 5: 예외를 다시 발생시키기 (re-raise)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   로그만 남기고 예외를 다시 위로 전달해야 할 때:
    #
    #   try:
    #       risky_operation()
    #   except ValueError as e:
    #       logging.error(f"에러 발생: {e}")
    #       raise    # ← 다시 위로 던지기!
    #

    print("  ★ 규칙 5: 로그만 남기고 re-raise 하기!")

    def safe_divide(a, b):
        try:
            return a / b
        except ZeroDivisionError as e:
            print(f"    [로그] 0으로 나누기 시도: {a}/{b}")
            raise    # 다시 위로 던짐!

    try:
        safe_divide(10, 0)
    except ZeroDivisionError:
        print("    [상위] 에러를 다시 받아서 처리!")

    # ── 실전 패턴: 재시도 (Retry) ──
    print("\n  [실전: 재시도 패턴]")
    import random

    def unreliable_operation():
        """70% 확률로 실패하는 함수"""
        if random.random() < 0.7:
            raise ConnectionError("서버 연결 실패!")
        return "성공!"

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            result = unreliable_operation()
            print(f"    시도 {attempt}: {result}")
            break
        except ConnectionError as e:
            print(f"    시도 {attempt}: 실패 → {e}")
            if attempt == max_retries:
                print("    → 최대 재시도 횟수 초과! 포기!")
    print()


def lesson10_student_grade_system():
    # =========================================================================
    #
    #   레슨 10 — 실전: 학생 성적 파일 관리 시스템
    #
    # =========================================================================
    print("┌──────────────────────────────────────┐")
    print("│  레슨 10 : 학생 성적 관리 시스템     │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 프로젝트: CSV로 성적 저장/조회/분석하는 시스템
    # ─────────────────────────────────────────────────────────────────────
    #
    #   기능:
    #     1. 학생 성적 추가
    #     2. 성적 파일 저장 (CSV)
    #     3. 성적 파일 불러오기
    #     4. 통계 분석 (평균, 최고점, 최저점)
    #     5. JSON으로 리포트 저장
    #

    class InvalidScoreError(Exception):
        """유효하지 않은 점수"""
        def __init__(self, score):
            super().__init__(f"유효하지 않은 점수: {score} (0~100만 가능)")
            self.score = score

    class StudentNotFoundError(Exception):
        """학생을 찾을 수 없음"""
        pass

    class GradeManager:
        """학생 성적 관리 클래스"""

        def __init__(self):
            self.students = {}   # {"민수": {"국어": 95, "수학": 88}, ...}

        def add_score(self, name, subject, score):
            """학생의 과목 점수를 추가/수정"""
            # 점수 유효성 검사
            if not isinstance(score, (int, float)):
                raise TypeError(f"점수는 숫자여야 합니다: {score}")
            if score < 0 or score > 100:
                raise InvalidScoreError(score)

            if name not in self.students:
                self.students[name] = {}
            self.students[name][subject] = score

        def get_student(self, name):
            """학생 정보 조회"""
            if name not in self.students:
                raise StudentNotFoundError(f"학생을 찾을 수 없음: {name}")
            return self.students[name]

        def save_csv(self, filepath):
            """CSV 파일로 저장"""
            # 모든 과목 수집
            subjects = set()
            for scores in self.students.values():
                subjects.update(scores.keys())
            subjects = sorted(subjects)

            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["이름"] + subjects)    # 헤더
                for name, scores in self.students.items():
                    row = [name] + [scores.get(s, "") for s in subjects]
                    writer.writerow(row)

        def load_csv(self, filepath):
            """CSV 파일에서 불러오기"""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    subjects = header[1:]    # 첫 번째 열은 이름

                    self.students = {}
                    for row in reader:
                        name = row[0]
                        self.students[name] = {}
                        for i, subject in enumerate(subjects):
                            if row[i + 1]:    # 빈 값이 아니면
                                try:
                                    self.students[name][subject] = float(row[i + 1])
                                except ValueError:
                                    print(f"    경고: {name}의 {subject} 점수 변환 실패")
            except FileNotFoundError:
                print(f"    파일을 찾을 수 없습니다: {filepath}")
                print("    빈 데이터로 시작합니다.")
                self.students = {}

        def get_statistics(self):
            """전체 통계 계산"""
            if not self.students:
                return {"학생 수": 0, "메시지": "데이터 없음"}

            stats = {"학생 수": len(self.students), "학생별_통계": {}}

            for name, scores in self.students.items():
                if scores:
                    values = list(scores.values())
                    stats["학생별_통계"][name] = {
                        "과목 수": len(values),
                        "총점": sum(values),
                        "평균": round(sum(values) / len(values), 1),
                        "최고점": max(values),
                        "최저점": min(values),
                    }
            return stats

        def save_report_json(self, filepath):
            """JSON으로 리포트 저장"""
            report = {
                "제목": "학생 성적 분석 리포트",
                "통계": self.get_statistics(),
                "전체_데이터": self.students,
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

    # ── 실제 사용 ──
    with tempfile.TemporaryDirectory() as tmp:
        manager = GradeManager()

        # 성적 추가
        print("  [1] 성적 추가")
        test_data = [
            ("민수", "국어", 95), ("민수", "수학", 88), ("민수", "영어", 92),
            ("지유", "국어", 100), ("지유", "수학", 97), ("지유", "영어", 95),
            ("서연", "국어", 88), ("서연", "수학", 92), ("서연", "영어", 85),
        ]
        for name, subject, score in test_data:
            manager.add_score(name, subject, score)
        print(f"    {len(test_data)}건 추가 완료!")

        # 잘못된 데이터 테스트
        print("\n  [2] 잘못된 데이터 처리")
        bad_data = [("하준", "국어", 150), ("하준", "수학", -10)]
        for name, subject, score in bad_data:
            try:
                manager.add_score(name, subject, score)
            except InvalidScoreError as e:
                print(f"    에러: {e}")

        # CSV 저장/불러오기
        csv_path = os.path.join(tmp, "grades.csv")
        manager.save_csv(csv_path)
        print(f"\n  [3] CSV 저장 완료: {Path(csv_path).name}")

        # CSV 내용 확인
        with open(csv_path, 'r', encoding='utf-8') as f:
            print(f"    내용:\n    {f.read().strip().replace(chr(10), chr(10) + '    ')}")

        # 새 매니저로 불러오기
        manager2 = GradeManager()
        manager2.load_csv(csv_path)
        print(f"\n  [4] CSV 불러오기 완료: {len(manager2.students)}명")

        # 통계
        print("\n  [5] 통계 분석")
        stats = manager2.get_statistics()
        for name, info in stats["학생별_통계"].items():
            print(f"    {name}: 평균={info['평균']}, 최고={info['최고점']}, 최저={info['최저점']}")

        # 존재하지 않는 학생 조회
        print("\n  [6] 존재하지 않는 학생 조회")
        try:
            manager2.get_student("없는학생")
        except StudentNotFoundError as e:
            print(f"    에러: {e}")

        # JSON 리포트
        json_path = os.path.join(tmp, "report.json")
        manager2.save_report_json(json_path)
        print(f"\n  [7] JSON 리포트 저장 완료!")
        with open(json_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        print(f"    리포트 제목: {report['제목']}")
        print(f"    학생 수: {report['통계']['학생 수']}명")
    print()


def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 07단계: 파일 입출력과 예외 처리")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")

    lesson1_file_open_close()
    lesson2_read_text_file()
    lesson3_write_text_file()
    lesson4_file_paths()
    lesson5_csv_json()
    lesson6_exception_basics()
    lesson7_exception_types()
    lesson8_custom_exceptions()
    lesson9_best_practices()
    lesson10_student_grade_system()

    print("\n  ★ 07단계 학습 완료!")
    print("  → 다음 단계: 08_iterators_generators.py")


if __name__ == "__main__":
    main()
