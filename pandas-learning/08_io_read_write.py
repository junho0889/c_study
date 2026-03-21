# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 08단계: 파일 입출력 (I/O)
#   ─ CSV, Excel, JSON, SQL, Parquet, 대용량 처리 ─
#   ■ 실행 방법: python 08_io_read_write.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  데이터는 파일에서 읽고 파일로 저장해요!
# =========================================================================
#
#  데이터 분석의 시작 = 파일 읽기
#  데이터 분석의 끝   = 결과 저장
#
#  Pandas가 지원하는 주요 파일 형식:
#    CSV    — 가장 흔한 텍스트 형식
#    Excel  — 엑셀 스프레드시트
#    JSON   — 웹/API에서 많이 쓰는 형식
#    SQL    — 데이터베이스
#    Parquet — 빅데이터에서 쓰는 고성능 형식
# =========================================================================

print("=" * 70)
print(" 08단계: 파일 입출력 (I/O)")
print("=" * 70)

import os
import json


# ─────────────────────────────────────────────────────────────────────────
# 1. CSV — 가장 흔한 데이터 형식
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. CSV (Comma-Separated Values)")
print("─" * 70)

print("""
  CSV란?
  → 쉼표(,)로 구분된 텍스트 파일
  → 엑셀에서도 열 수 있고, 메모장에서도 열 수 있어요!

  예시 (students.csv):
    이름,수학,영어,국어
    김민수,90,78,85
    이영희,88,95,85

  Pandas로 읽기: pd.read_csv('파일명.csv')
  Pandas로 쓰기: df.to_csv('파일명.csv')
""")


# ── CSV 쓰기 (순수 파이썬) ──
def write_csv(filename, headers, rows, sep=',', encoding='utf-8'):
    """
    CSV 파일 쓰기 — 순수 파이썬 구현.

    Pandas에서:
      df.to_csv('파일명.csv', index=False, encoding='utf-8')
    """
    with open(filename, 'w', encoding=encoding) as f:
        # 헤더 쓰기
        f.write(sep.join(str(h) for h in headers) + '\n')
        # 데이터 쓰기
        for row in rows:
            f.write(sep.join(str(v) for v in row) + '\n')
    print(f"  → '{filename}' 저장 완료 ({len(rows)}행)")


# ── CSV 읽기 (순수 파이썬) ──
def read_csv(filename, sep=',', encoding='utf-8', header=0,
             usecols=None, dtype=None, skiprows=None, nrows=None):
    """
    CSV 파일 읽기 — 순수 파이썬 구현.

    Pandas read_csv() 주요 옵션:
      sep          구분자 (기본 ',', TSV는 '\\t')
      header       헤더 행 번호 (기본 0, None이면 헤더 없음)
      encoding     인코딩 (utf-8, euc-kr, cp949 등)
      usecols      읽을 열 선택 ['이름', '수학']
      dtype        데이터 타입 지정 {'학번': str}
      skiprows     건너뛸 행 수
      nrows        읽을 행 수
      parse_dates  날짜로 파싱할 열 ['날짜']
      na_values    결측값으로 취급할 값 ['N/A', '없음']
      index_col    인덱스로 쓸 열 '학번'
    """
    data = {}
    with open(filename, 'r', encoding=encoding) as f:
        lines = f.readlines()

    # skiprows 처리
    if skiprows:
        lines = lines[skiprows:]

    # 헤더 파싱
    if header is not None:
        headers = lines[header].strip().split(sep)
        data_lines = lines[header + 1:]
    else:
        data_lines = lines
        headers = [f'col_{i}' for i in range(len(lines[0].strip().split(sep)))]

    # nrows 제한
    if nrows:
        data_lines = data_lines[:nrows]

    # usecols 필터링
    if usecols:
        col_indices = [headers.index(c) for c in usecols if c in headers]
        headers = [headers[i] for i in col_indices]
    else:
        col_indices = list(range(len(headers)))

    # 데이터 파싱
    for h in headers:
        data[h] = []

    for line in data_lines:
        values = line.strip().split(sep)
        if len(values) >= len(col_indices):
            for hi, ci in enumerate(col_indices):
                val = values[ci] if ci < len(values) else ''
                # dtype 변환
                if dtype and headers[hi] in dtype:
                    target_type = dtype[headers[hi]]
                    try:
                        val = target_type(val)
                    except (ValueError, TypeError):
                        pass
                else:
                    # 자동 타입 추론
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                data[headers[hi]].append(val)

    print(f"  → '{filename}' 읽기 완료 ({len(data_lines)}행, {len(headers)}열)")
    return data, headers


# CSV 쓰기 예제
print("\n[CSV 쓰기]")
headers = ['이름', '학년', '수학', '영어', '국어']
rows = [
    ['김민수', 3, 90, 78, 85],
    ['이영희', 3, 88, 95, 85],
    ['박철수', 2, 65, 82, 90],
    ['최지영', 3, 98, 90, 82],
    ['정하늘', 2, 72, 85, 88],
]

csv_file = 'sample_students.csv'
write_csv(csv_file, headers, rows)

# ── Pandas로 하면? ──
# df.to_csv('sample_students.csv', index=False, encoding='utf-8')
# 옵션들:
#   index=False     → 인덱스 저장 안 함 (보통 False)
#   encoding='utf-8' → 한글 인코딩
#   sep='\t'        → 탭으로 구분 (TSV)
#   float_format='%.2f' → 소수점 2자리

# CSV 읽기 예제
print("\n[CSV 읽기] 전체 읽기:")
data, cols = read_csv(csv_file)
for col in cols:
    print(f"  {col}: {data[col]}")

# ── Pandas: df = pd.read_csv('sample_students.csv') ──

# 특정 열만 읽기
print("\n[CSV 읽기] 이름, 수학만 읽기 (usecols):")
data2, cols2 = read_csv(csv_file, usecols=['이름', '수학'])
for col in cols2:
    print(f"  {col}: {data2[col]}")
# ── Pandas: pd.read_csv('file.csv', usecols=['이름', '수학']) ──

# 처음 3행만 읽기
print("\n[CSV 읽기] 처음 3행만 (nrows=3):")
data3, cols3 = read_csv(csv_file, nrows=3)
for col in cols3:
    print(f"  {col}: {data3[col]}")
# ── Pandas: pd.read_csv('file.csv', nrows=3) ──

print("""
  💡 read_csv() 자주 쓰는 옵션 TOP 10:
  ┌──────────────┬────────────────────────────────────┐
  │ 옵션         │ 설명                               │
  ├──────────────┼────────────────────────────────────┤
  │ sep=','      │ 구분자 (TSV: '\\t')                │
  │ header=0     │ 헤더 행 (None이면 헤더 없음)       │
  │ encoding     │ 인코딩 (euc-kr, utf-8)             │
  │ usecols      │ 읽을 열 선택                       │
  │ dtype        │ 데이터 타입 지정                   │
  │ parse_dates  │ 날짜 파싱할 열                     │
  │ index_col    │ 인덱스로 쓸 열                     │
  │ na_values    │ 결측값으로 취급할 문자열            │
  │ nrows        │ 읽을 행 수 제한                    │
  │ skiprows     │ 건너뛸 행                          │
  └──────────────┴────────────────────────────────────┘
""")


# ─────────────────────────────────────────────────────────────────────────
# 2. Excel — 엑셀 스프레드시트
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 2. Excel 파일")
print("─" * 70)

print("""
  Pandas는 엑셀 파일도 읽고 쓸 수 있어요!

  필요 라이브러리:
    읽기: openpyxl (xlsx) 또는 xlrd (xls)
    쓰기: openpyxl
    pip install openpyxl

  읽기: pd.read_excel('파일.xlsx')
  쓰기: df.to_excel('파일.xlsx')
""")

# ── Pandas Excel 코드 (주석) ──
# # 기본 읽기
# df = pd.read_excel('성적표.xlsx')
#
# # 특정 시트 읽기
# df = pd.read_excel('성적표.xlsx', sheet_name='3학년')
# df = pd.read_excel('성적표.xlsx', sheet_name=0)  # 첫 번째 시트
#
# # 모든 시트 읽기 (딕셔너리로 반환)
# all_sheets = pd.read_excel('성적표.xlsx', sheet_name=None)
# for sheet_name, df in all_sheets.items():
#     print(f"시트: {sheet_name}, 행수: {len(df)}")
#
# # 엑셀로 저장
# df.to_excel('결과.xlsx', index=False)
#
# # 여러 시트로 저장
# with pd.ExcelWriter('결과.xlsx') as writer:
#     df1.to_excel(writer, sheet_name='1학년', index=False)
#     df2.to_excel(writer, sheet_name='2학년', index=False)
#     df3.to_excel(writer, sheet_name='3학년', index=False)

print("  (엑셀 파일은 openpyxl 라이브러리가 필요하므로 주석으로 설명)")
print("  → 위의 주석을 참고하세요!")


# ─────────────────────────────────────────────────────────────────────────
# 3. JSON — 웹/API 데이터 형식
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. JSON (JavaScript Object Notation)")
print("─" * 70)

print("""
  JSON은 웹에서 가장 많이 쓰는 데이터 형식이에요!
  API 호출 결과는 대부분 JSON으로 옵니다.

  JSON 구조:
    [
      {"이름": "민수", "수학": 90},
      {"이름": "영희", "수학": 88}
    ]
""")

# JSON 쓰기
def write_json(filename, data, orient='records'):
    """
    JSON 파일 쓰기.

    Pandas orient 옵션:
      'records' → [{"이름":"민수","수학":90}, ...]   (가장 직관적)
      'columns' → {"이름":["민수","영희"], "수학":[90,88]}
      'index'   → {"0":{"이름":"민수","수학":90}, ...}
      'split'   → {"columns":[...], "data":[[...],[...]]}
    """
    if orient == 'records':
        # 각 행을 하나의 딕셔너리로
        records = []
        headers = list(data.keys())
        n = len(data[headers[0]])
        for i in range(n):
            record = {h: data[h][i] for h in headers}
            records.append(record)
        output = records
    elif orient == 'columns':
        output = data
    else:
        output = data

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  → '{filename}' 저장 완료 (orient='{orient}')")


# JSON 읽기
def read_json(filename, orient='records'):
    """
    JSON 파일 읽기.

    Pandas에서:
      pd.read_json('파일.json')
      pd.read_json('파일.json', orient='records')
    """
    with open(filename, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    if orient == 'records' and isinstance(raw, list):
        headers = list(raw[0].keys()) if raw else []
        data = {h: [] for h in headers}
        for record in raw:
            for h in headers:
                data[h].append(record.get(h))
        return data, headers
    elif orient == 'columns' and isinstance(raw, dict):
        return raw, list(raw.keys())
    return raw, []


# 쓰기 예제
sample_data = {
    '이름': ['김민수', '이영희', '박철수'],
    '수학': [90, 88, 65],
    '영어': [78, 95, 82],
}

json_file = 'sample_students.json'
write_json(json_file, sample_data, orient='records')

# 파일 내용 확인
print("\n[JSON 파일 내용]")
with open(json_file, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 읽기 예제
print("[JSON 읽기]")
data, cols = read_json(json_file, orient='records')
for col in cols:
    print(f"  {col}: {data[col]}")
# ── Pandas: df = pd.read_json('sample_students.json') ──

# columns orient
json_file2 = 'sample_columns.json'
write_json(json_file2, sample_data, orient='columns')
print("\n[columns orient 내용]")
with open(json_file2, 'r', encoding='utf-8') as f:
    print(f.read())


# ─────────────────────────────────────────────────────────────────────────
# 4. SQL — 데이터베이스
# ─────────────────────────────────────────────────────────────────────────

print("─" * 70)
print(" 4. SQL (데이터베이스 연동)")
print("─" * 70)

print("""
  Pandas는 SQL 데이터베이스에서 직접 데이터를 읽을 수 있어요!

  필요: SQLAlchemy + 데이터베이스 드라이버

  # SQLite 예시 (파일 기반, 설치 불필요)
  import sqlite3
  conn = sqlite3.connect('school.db')

  # 읽기
  df = pd.read_sql('SELECT * FROM students', conn)
  df = pd.read_sql_query('SELECT 이름, 수학 FROM students WHERE 수학 > 80', conn)
  df = pd.read_sql_table('students', conn)  # 테이블 전체

  # 쓰기
  df.to_sql('students', conn, if_exists='replace', index=False)
  # if_exists: 'fail'(에러), 'replace'(덮어쓰기), 'append'(추가)

  # PostgreSQL/MySQL 예시
  from sqlalchemy import create_engine
  engine = create_engine('postgresql://user:pass@host:5432/dbname')
  df = pd.read_sql('SELECT * FROM table', engine)
""")

# SQLite 시뮬레이션 (순수 파이썬)
print("\n[SQL 시뮬레이션] SELECT * FROM students WHERE 수학 > 80:")
students_table = [
    {'이름': '김민수', '학년': 3, '수학': 90, '영어': 78},
    {'이름': '이영희', '학년': 3, '수학': 88, '영어': 95},
    {'이름': '박철수', '학년': 2, '수학': 65, '영어': 82},
    {'이름': '최지영', '학년': 3, '수학': 98, '영어': 90},
]

# WHERE 수학 > 80
filtered = [row for row in students_table if row['수학'] > 80]
for row in filtered:
    print(f"  {row}")


# ─────────────────────────────────────────────────────────────────────────
# 5. Parquet — 고성능 열 기반 저장 형식
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. Parquet — 빅데이터의 표준 형식")
print("─" * 70)

print("""
  Parquet이 뭐예요?
  → Apache에서 만든 "열 기반(columnar)" 저장 형식

  CSV vs Parquet:

  ┌─ CSV (행 기반) ───────────────────────────┐
  │ 민수, 90, 78, 85                          │
  │ 영희, 88, 95, 85                          │
  │ 철수, 65, 82, 90                          │
  │                                            │
  │ → 행 단위로 저장                           │
  │ → "수학 열만 읽기"도 전체 파일을 읽어야!   │
  │ → 텍스트라 용량 큼, 타입 정보 없음         │
  └────────────────────────────────────────────┘

  ┌─ Parquet (열 기반) ───────────────────────┐
  │ [이름: 민수, 영희, 철수]                   │
  │ [수학: 90, 88, 65]                         │
  │ [영어: 78, 95, 82]                         │
  │ [국어: 85, 85, 90]                         │
  │                                            │
  │ → 열 단위로 저장                           │
  │ → "수학 열만 읽기" 가능! (훨씬 빠름)      │
  │ → 압축률 높음 (같은 타입끼리 모여있어서)   │
  │ → 타입 정보 자동 저장                      │
  └────────────────────────────────────────────┘

  Parquet의 장점:
    1) 압축: CSV 대비 50~90% 작은 파일 크기
    2) 속도: 필요한 열만 읽어서 빠름
    3) 타입: 데이터 타입이 보존됨
    4) 호환: Python, R, Java, Spark 모두 지원

  사용법:
    pip install pyarrow  (또는 fastparquet)
    df.to_parquet('data.parquet')
    df = pd.read_parquet('data.parquet')
    df = pd.read_parquet('data.parquet', columns=['수학', '영어'])  # 열 선택!
""")

# 파일 크기 비교 시뮬레이션
print("\n[파일 크기 비교 시뮬레이션]")
n_rows = 100000
csv_size = n_rows * 30  # 행당 약 30바이트
parquet_size = n_rows * 8  # 열 기반 + 압축

print(f"  {n_rows:,}행 데이터:")
print(f"    CSV:     {csv_size / 1024 / 1024:.1f} MB (예상)")
print(f"    Parquet: {parquet_size / 1024 / 1024:.1f} MB (예상)")
print(f"    절감률:  {(1 - parquet_size / csv_size) * 100:.0f}%")


# ─────────────────────────────────────────────────────────────────────────
# 6. 대용량 파일 처리 — chunksize
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 대용량 파일 처리")
print("─" * 70)

print("""
  10GB 파일을 한번에 읽으면? → 메모리 부족 에러! 💥

  해결책 1: chunksize — 조금씩 나눠 읽기
  ┌──────────────────────────────────────────┐
  │ for chunk in pd.read_csv('big.csv',      │
  │                           chunksize=10000):│
  │     # chunk = 10000행짜리 DataFrame      │
  │     process(chunk)                        │
  └──────────────────────────────────────────┘

  해결책 2: dtype 최적화 — 메모리 사용량 줄이기
  ┌──────────────────────────────────────────┐
  │ 기본 int64 (8바이트) → int8 (1바이트)    │
  │ 기본 float64 → float32                   │
  │ 반복 문자열 → category 타입              │
  │                                           │
  │ df['학년'] = df['학년'].astype('int8')    │
  │ df['학교'] = df['학교'].astype('category')│
  └──────────────────────────────────────────┘
""")

# chunksize 시뮬레이션
print("\n[chunksize 시뮬레이션] 큰 CSV를 1000행씩 처리:")

# 큰 CSV 만들기
import random
random.seed(42)
big_file = 'sample_big.csv'
big_headers = ['ID', '이름', '점수']
big_rows = [[i, f'학생{i}', random.randint(0, 100)] for i in range(5000)]
write_csv(big_file, big_headers, big_rows)

# chunksize로 읽기
chunk_size = 1000
total_sum = 0
total_count = 0
chunk_num = 0

with open(big_file, 'r', encoding='utf-8') as f:
    header_line = f.readline()  # 헤더 건너뛰기
    chunk = []
    for line in f:
        chunk.append(line.strip().split(','))
        if len(chunk) >= chunk_size:
            chunk_num += 1
            scores = [int(row[2]) for row in chunk]
            total_sum += sum(scores)
            total_count += len(scores)
            avg = sum(scores) / len(scores)
            print(f"    청크 {chunk_num}: {len(chunk)}행 처리, 평균={avg:.1f}")
            chunk = []

    # 마지막 청크
    if chunk:
        chunk_num += 1
        scores = [int(row[2]) for row in chunk]
        total_sum += sum(scores)
        total_count += len(scores)
        avg = sum(scores) / len(scores)
        print(f"    청크 {chunk_num}: {len(chunk)}행 처리, 평균={avg:.1f}")

overall_avg = total_sum / total_count
print(f"  → 전체 평균: {overall_avg:.1f} ({total_count}행)")

# ── Pandas로 하면? ──
# total = 0
# count = 0
# for chunk in pd.read_csv('big.csv', chunksize=1000):
#     total += chunk['점수'].sum()
#     count += len(chunk)
# print(f"전체 평균: {total/count:.1f}")

# dtype 최적화 예시
print("\n[dtype 최적화] 메모리 사용량 비교:")
print("""
  ┌──────────────┬──────────┬──────────┬────────────┐
  │ dtype        │ 범위     │ 바이트   │ 100만행 시 │
  ├──────────────┼──────────┼──────────┼────────────┤
  │ int64 (기본) │ ±9.2×10¹⁸│ 8 bytes  │ 7.6 MB     │
  │ int32        │ ±2.1×10⁹ │ 4 bytes  │ 3.8 MB     │
  │ int16        │ ±32,768  │ 2 bytes  │ 1.9 MB     │
  │ int8         │ ±128     │ 1 byte   │ 0.95 MB    │
  │              │          │          │            │
  │ float64(기본)│ 15자리   │ 8 bytes  │ 7.6 MB     │
  │ float32      │ 7자리    │ 4 bytes  │ 3.8 MB     │
  │              │          │          │            │
  │ object(문자) │ 가변     │ ~50+byte │ 47+ MB     │
  │ category     │ 가변     │ ~수 byte │ 1~5 MB     │
  └──────────────┴──────────┴──────────┴────────────┘

  학년(1~6): int8이면 충분! (int64의 1/8 메모리)
  학교이름: category로 바꾸면 수십 배 절약!
""")

# ── Pandas: ──
# df = pd.read_csv('big.csv', dtype={'학년': 'int8', '학교': 'category'})
# print(df.memory_usage(deep=True))
# df.info(memory_usage='deep')


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 다양한 형식 변환 파이프라인
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 다양한 형식 변환 파이프라인")
print("═" * 70)

# 1단계: 원본 데이터 생성
print("\n── 1단계: 원본 데이터 생성 ──")
student_data = {
    '학번': ['S001', 'S002', 'S003', 'S004', 'S005'],
    '이름': ['김민수', '이영희', '박철수', '최지영', '정하늘'],
    '학년': [3, 3, 2, 3, 2],
    '수학': [90, 88, 65, 98, 72],
    '영어': [78, 95, 82, 90, 85],
    '국어': [85, 85, 90, 82, 88],
}

# 2단계: CSV로 저장
print("\n── 2단계: CSV로 저장 ──")
csv_out = 'pipeline_students.csv'
csv_headers = list(student_data.keys())
csv_rows = []
for i in range(len(student_data['학번'])):
    row = [student_data[col][i] for col in csv_headers]
    csv_rows.append(row)
write_csv(csv_out, csv_headers, csv_rows)

# 3단계: CSV 읽기 → 가공
print("\n── 3단계: CSV 읽기 → 가공 ──")
loaded, cols = read_csv(csv_out)
# 총점 추가
loaded['총점'] = [loaded['수학'][i] + loaded['영어'][i] + loaded['국어'][i]
                  for i in range(len(loaded['학번']))]
loaded['평균'] = [round(loaded['총점'][i] / 3, 1) for i in range(len(loaded['학번']))]

print("  가공된 데이터:")
for i in range(len(loaded['학번'])):
    print(f"    {loaded['이름'][i]}: 총점={loaded['총점'][i]}, 평균={loaded['평균'][i]}")

# 4단계: JSON으로 저장
print("\n── 4단계: JSON으로 저장 ──")
json_out = 'pipeline_students.json'
write_json(json_out, loaded, orient='records')

# 5단계: JSON 읽기 → 확인
print("\n── 5단계: JSON 읽기 → 확인 ──")
json_data, json_cols = read_json(json_out)
print(f"  열: {json_cols}")
print(f"  행 수: {len(json_data[json_cols[0]])}")

# 6단계: 파이프라인 요약
print("\n── 6단계: 파이프라인 요약 ──")
print(f"""
  ┌─────────────────────────────────────────────┐
  │ 데이터 파이프라인 완료!                     │
  │                                              │
  │ 원본 데이터 (dict)                           │
  │      ↓ write_csv()                           │
  │ {csv_out:<30}         │
  │      ↓ read_csv() + 가공                     │
  │ 총점, 평균 추가                              │
  │      ↓ write_json()                          │
  │ {json_out:<30}        │
  │                                              │
  │ Pandas로 하면?                               │
  │ df = pd.read_csv('{csv_out}')   │
  │ df['총점'] = df[['수학','영어','국어']].sum(1)│
  │ df.to_json('{json_out}')        │
  │                                              │
  │ → 3줄이면 끝!                               │
  └─────────────────────────────────────────────┘
""")

# 임시 파일 정리
for f in [csv_file, json_file, json_file2, big_file, csv_out, json_out]:
    try:
        os.remove(f)
    except FileNotFoundError:
        pass
print("  (임시 파일 정리 완료)")


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: 파일 I/O 도구 모음")
print("═" * 70)

print("""
  ┌──────────┬───────────────────┬────────────────────────┐
  │ 형식     │ 읽기              │ 쓰기                   │
  ├──────────┼───────────────────┼────────────────────────┤
  │ CSV      │ pd.read_csv()     │ df.to_csv()            │
  │ Excel    │ pd.read_excel()   │ df.to_excel()          │
  │ JSON     │ pd.read_json()    │ df.to_json()           │
  │ SQL      │ pd.read_sql()     │ df.to_sql()            │
  │ Parquet  │ pd.read_parquet() │ df.to_parquet()        │
  │ HTML표   │ pd.read_html()    │ df.to_html()           │
  │ 클립보드 │ pd.read_clipboard()│ df.to_clipboard()     │
  └──────────┴───────────────────┴────────────────────────┘

  대용량 처리:
  • chunksize로 나눠 읽기
  • dtype 최적화 (int8, category)
  • Parquet 사용 (압축 + 열 선택)
  • usecols로 필요한 열만 읽기
""")

print("✅ 08단계 완료! 다음은 09_visualization.py에서 시각화를 배워요!")
