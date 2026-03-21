# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   Pandas 학습 07단계: 문자열과 날짜/시간 처리
#   ─ str 접근자, 정규표현식, datetime, dt 접근자, resample ─
#   ■ 실행 방법: python 07_string_datetime.py
#   ■ Pandas 설치: pip install pandas
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# =========================================================================
#  문자열과 날짜는 데이터 분석의 필수 도구예요!
# =========================================================================
#
#  문자열 처리:
#    - 이름에서 성(姓)만 뽑기
#    - 이메일에서 도메인 추출
#    - 주소에서 "서울" 포함 여부 확인
#
#  날짜/시간 처리:
#    - "2024-03-15" → 몇 월? 무슨 요일?
#    - 월별/주별 매출 집계
#    - 날짜 차이 계산 (몇 일이나 지났나?)
# =========================================================================

print("=" * 70)
print(" 07단계: 문자열과 날짜/시간 처리")
print("=" * 70)

import re
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────
# 1. 문자열 처리 — str 접근자
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 1. 문자열 처리 (str 접근자)")
print("─" * 70)

print("""
  Pandas Series에서 문자열을 다루려면 .str 접근자를 써요!

  일반 파이썬: "hello".upper() → "HELLO"
  Pandas:      df['이름'].str.upper() → 모든 이름을 대문자로!

  .str은 "모든 원소에 동시에 문자열 메서드를 적용"하는 마법이에요.
""")

# 테스트 데이터
names = ['김민수', '이영희', '박철수 ', ' 최지영', '정 하늘']
emails = ['minsu@gmail.com', 'younghee@naver.com', 'chulsoo@daum.net',
          'jiyoung@gmail.com', 'haneul@yahoo.co.kr']
phones = ['010-1234-5678', '010-2345-6789', '011-3456-7890',
          '010-4567-8901', '010-5678-9012']
addresses = ['서울시 강남구 역삼동', '부산시 해운대구', '서울시 서초구 반포동',
             '대전시 유성구', '서울시 마포구 합정동']


# ── str.upper() / str.lower() ──
print("\n[str.upper()] 대문자 변환 (영문):")
upper_emails = [e.upper() for e in emails]
for orig, upper in zip(emails, upper_emails):
    print(f"  {orig:>25} → {upper}")
# ── Pandas: df['이메일'].str.upper() ──

# ── str.strip() / str.lstrip() / str.rstrip() ──
print("\n[str.strip()] 공백 제거:")
stripped = [n.strip() for n in names]
for orig, clean in zip(names, stripped):
    print(f"  '{orig}' → '{clean}'")
# ── Pandas: df['이름'].str.strip() ──

# ── str.len() ──
print("\n[str.len()] 문자열 길이:")
lengths = [len(n.strip()) for n in names]
for name, length in zip(stripped, lengths):
    print(f"  {name}: {length}글자")
# ── Pandas: df['이름'].str.len() ──

# ── str.contains() ──
print("\n[str.contains()] '서울' 포함 여부:")
contains_seoul = ['서울' in addr for addr in addresses]
for addr, result in zip(addresses, contains_seoul):
    print(f"  {addr:>20} → {'서울 포함!' if result else '포함 안됨'}")
# ── Pandas: df['주소'].str.contains('서울') ──

# ── str.startswith() / str.endswith() ──
print("\n[str.startswith()] '010'으로 시작하는 전화번호:")
starts_010 = [p.startswith('010') for p in phones]
for phone, result in zip(phones, starts_010):
    print(f"  {phone} → {'010!' if result else '다른 번호'}")
# ── Pandas: df['전화'].str.startswith('010') ──

# ── str.replace() ──
print("\n[str.replace()] 전화번호에서 '-' 제거:")
replaced = [p.replace('-', '') for p in phones]
for orig, clean in zip(phones, replaced):
    print(f"  {orig} → {clean}")
# ── Pandas: df['전화'].str.replace('-', '', regex=False) ──

# ── str.split() ──
print("\n[str.split()] 이메일을 '@'로 분리:")
splits = [e.split('@') for e in emails]
for email, parts in zip(emails, splits):
    print(f"  {email:>25} → 아이디: {parts[0]}, 도메인: {parts[1]}")
# ── Pandas: df['이메일'].str.split('@') → 리스트의 Series
# ── Pandas: df['이메일'].str.split('@', expand=True) → 열로 분리!

# ── str.slice() / str[n:m] ──
print("\n[str[:1]] 이름에서 성(姓)만 추출:")
last_names = [n.strip()[0] for n in names]
for name, ln in zip(stripped, last_names):
    print(f"  {name} → 성: {ln}")
# ── Pandas: df['이름'].str[0] ──
# ── Pandas: df['이름'].str[:1] ──  (slice)

# ── str.cat() ──
print("\n[str.cat()] 문자열 합치기:")
greetings = [f"{n}님 안녕하세요!" for n in stripped]
for g in greetings:
    print(f"  {g}")
# ── Pandas: df['이름'].str.cat(['님'] * 5) ──
# ── 또는: df['이름'] + '님 안녕하세요!' ──


# ─────────────────────────────────────────────────────────────────────────
# 2. 정규표현식 — str.extract(), str.findall()
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 2. 정규표현식 (Regex)")
print("─" * 70)

print("""
  정규표현식은 "문자열 패턴"을 찾는 도구예요!

  \\d     → 숫자 한 글자        [0-9]
  \\d+    → 숫자 하나 이상      010, 1234
  \\w     → 글자 한 글자        a, 가
  .      → 아무 글자 하나
  [A-Z]  → 대문자 영어 한 글자
  (...)  → 그룹 (추출할 부분)
""")

# str.extract() — 패턴에서 그룹 추출
print("\n[str.extract()] 전화번호에서 지역번호 추출:")
for phone in phones:
    match = re.match(r'(\d{3})-(\d{4})-(\d{4})', phone)
    if match:
        area = match.group(1)
        mid = match.group(2)
        last = match.group(3)
        print(f"  {phone} → 지역: {area}, 중간: {mid}, 끝: {last}")
# ── Pandas: df['전화'].str.extract(r'(\d{3})-(\d{4})-(\d{4})') ──
# → 3개 열의 DataFrame 반환!

# 이메일에서 아이디와 도메인 추출
print("\n[str.extract()] 이메일에서 아이디/도메인 추출:")
for email in emails:
    match = re.match(r'(\w+)@([\w.]+)', email)
    if match:
        print(f"  {email:>25} → ID: {match.group(1)}, 도메인: {match.group(2)}")
# ── Pandas: df['이메일'].str.extract(r'(\w+)@([\w.]+)') ──

# str.findall() — 패턴 모두 찾기
print("\n[str.findall()] 주소에서 모든 숫자 찾기:")
addresses_with_nums = ['서울시 강남구 역삼동 123-45', '부산시 해운대구 456번지',
                       '대전시 유성구 789-12호']
for addr in addresses_with_nums:
    numbers = re.findall(r'\d+', addr)
    print(f"  {addr} → 숫자들: {numbers}")
# ── Pandas: df['주소'].str.findall(r'\d+') ──

# str.contains() with regex
print("\n[str.contains()] 정규식으로 '서울|부산' 검색:")
for addr in addresses:
    match = bool(re.search(r'서울|부산', addr))
    print(f"  {addr:>20} → {'매칭!' if match else '미매칭'}")
# ── Pandas: df['주소'].str.contains(r'서울|부산', regex=True) ──


# ─────────────────────────────────────────────────────────────────────────
# 3. 날짜/시간 기본 — datetime
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 3. 날짜/시간 기본 (datetime)")
print("─" * 70)

print("""
  Pandas는 날짜를 다루는 강력한 도구를 제공해요!

  문자열 → datetime 변환:
    pd.to_datetime('2024-03-15') → Timestamp('2024-03-15')

  datetime에서 정보 추출:
    .dt.year   → 연도
    .dt.month  → 월
    .dt.day    → 일
    .dt.day_name() → 요일 이름
""")

# 문자열 → datetime 변환
date_strings = ['2024-03-15', '2024-04-20', '2024-05-10',
                '2024-06-01', '2024-07-25']

print("\n[to_datetime()] 문자열 → datetime 변환:")
dates = [datetime.strptime(d, '%Y-%m-%d') for d in date_strings]
for ds, dt in zip(date_strings, dates):
    print(f"  '{ds}' → {dt}")
# ── Pandas: pd.to_datetime(df['날짜']) ──

# datetime에서 정보 추출
print("\n[dt 접근자] 날짜 정보 추출:")
weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
for dt in dates:
    year = dt.year
    month = dt.month
    day = dt.day
    weekday = weekday_names[dt.weekday()]
    quarter = (month - 1) // 3 + 1
    print(f"  {dt.strftime('%Y-%m-%d')}: {year}년 {month}월 {day}일 ({weekday}), Q{quarter}")
# ── Pandas: ──
# df['날짜'].dt.year
# df['날짜'].dt.month
# df['날짜'].dt.day
# df['날짜'].dt.day_name()
# df['날짜'].dt.quarter

# 다양한 날짜 형식 파싱
print("\n[다양한 날짜 형식]")
various_formats = [
    ('2024/03/15', '%Y/%m/%d'),
    ('15-03-2024', '%d-%m-%Y'),
    ('Mar 15, 2024', '%b %d, %Y'),
    ('20240315', '%Y%m%d'),
]
for date_str, fmt in various_formats:
    parsed = datetime.strptime(date_str, fmt)
    print(f"  '{date_str}' (형식: {fmt}) → {parsed.strftime('%Y-%m-%d')}")
# ── Pandas: pd.to_datetime(df['날짜'], format='%Y/%m/%d') ──
# ── Pandas: pd.to_datetime(df['날짜'], format='mixed')  (자동 추론) ──


# ─────────────────────────────────────────────────────────────────────────
# 4. Timedelta — 날짜 연산
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 4. Timedelta — 날짜 연산")
print("─" * 70)

print("""
  Timedelta = 두 날짜/시간 사이의 "차이"

  날짜1 - 날짜2 = Timedelta (며칠 차이)
  날짜 + Timedelta = 새 날짜 (며칠 후)
""")

# 날짜 차이 계산
start = datetime(2024, 3, 1)
end = datetime(2024, 3, 15)
diff = end - start
print(f"\n  시작: {start.strftime('%Y-%m-%d')}")
print(f"  끝:   {end.strftime('%Y-%m-%d')}")
print(f"  차이: {diff.days}일")
# ── Pandas: df['끝'] - df['시작'] → Timedelta Series ──

# 날짜 더하기/빼기
base_date = datetime(2024, 3, 15)
after_7 = base_date + timedelta(days=7)
before_30 = base_date - timedelta(days=30)
print(f"\n  기준일: {base_date.strftime('%Y-%m-%d')}")
print(f"  7일 후: {after_7.strftime('%Y-%m-%d')}")
print(f"  30일 전: {before_30.strftime('%Y-%m-%d')}")
# ── Pandas: df['날짜'] + pd.Timedelta(days=7) ──
# ── Pandas: df['날짜'] - pd.Timedelta(days=30) ──

# D-day 계산
events = [
    ('개학', datetime(2024, 3, 4)),
    ('중간고사', datetime(2024, 4, 22)),
    ('기말고사', datetime(2024, 7, 1)),
    ('방학', datetime(2024, 7, 20)),
]
today = datetime(2024, 3, 15)
print(f"\n  [D-day 계산] 오늘: {today.strftime('%Y-%m-%d')}")
for name, date in events:
    diff = (date - today).days
    if diff > 0:
        print(f"    {name}: D-{diff}")
    elif diff == 0:
        print(f"    {name}: D-Day!")
    else:
        print(f"    {name}: D+{abs(diff)} (지남)")


# ─────────────────────────────────────────────────────────────────────────
# 5. DatetimeIndex와 resample()
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 5. DatetimeIndex와 resample()")
print("─" * 70)

print("""
  DatetimeIndex는 날짜를 인덱스로 사용하는 것!

  장점:
    - 날짜로 바로 슬라이싱: df['2024-03']
    - resample(): 월별/주별 집계 (GroupBy의 시계열 버전)

  resample() 주기:
    'D' → 일별, 'W' → 주별, 'M' → 월별
    'Q' → 분기별, 'Y' → 연별, 'H' → 시간별
""")

# 일별 매출 데이터 생성
import random
random.seed(42)

daily_dates = []
daily_sales = []
daily_visitors = []

base = datetime(2024, 1, 1)
for i in range(90):  # 1월~3월
    date = base + timedelta(days=i)
    daily_dates.append(date.strftime('%Y-%m-%d'))
    daily_sales.append(random.randint(50, 200) * 1000)
    daily_visitors.append(random.randint(30, 150))

print(f"\n  일별 매출 데이터: {len(daily_dates)}일치")
print(f"  기간: {daily_dates[0]} ~ {daily_dates[-1]}")

# 날짜로 슬라이싱 (특정 달)
print("\n[날짜 슬라이싱] 2024년 2월 데이터:")
feb_data = [(d, s, v) for d, s, v in zip(daily_dates, daily_sales, daily_visitors)
            if d.startswith('2024-02')]
print(f"  2월 데이터: {len(feb_data)}일")
print(f"  2월 총 매출: {sum(s for _, s, _ in feb_data):,}원")
# ── Pandas: df['2024-02'] (DatetimeIndex일 때 바로 슬라이싱!) ──

# resample 시뮬레이션 — 월별 집계
print("\n[resample('M')] 월별 매출 집계:")
monthly = {}
for d, s, v in zip(daily_dates, daily_sales, daily_visitors):
    month = d[:7]  # '2024-01'
    if month not in monthly:
        monthly[month] = {'매출': 0, '방문자': 0, '일수': 0}
    monthly[month]['매출'] += s
    monthly[month]['방문자'] += v
    monthly[month]['일수'] += 1

for month, data in sorted(monthly.items()):
    avg_daily = data['매출'] // data['일수']
    bar = "█" * (data['매출'] // 500000)
    print(f"  {month}: 총 {data['매출']:>12,}원 "
          f"(일평균 {avg_daily:>9,}원) {bar}")
# ── Pandas: df.resample('M').sum() ──  (DatetimeIndex 필요)
# ── 또는: df.resample('ME').sum() ──  (Pandas 2.1+)

# 주별 집계
print("\n[resample('W')] 주별 방문자 집계 (1월만):")
weekly = {}
for d, _, v in zip(daily_dates, daily_sales, daily_visitors):
    if not d.startswith('2024-01'):
        continue
    dt = datetime.strptime(d, '%Y-%m-%d')
    week_num = dt.isocalendar()[1]
    week_key = f"W{week_num:02d}"
    if week_key not in weekly:
        weekly[week_key] = 0
    weekly[week_key] += v

for week, total in sorted(weekly.items()):
    bar = "▓" * (total // 50)
    print(f"  {week}: {total:>4}명 {bar}")
# ── Pandas: df.resample('W').sum() ──


# ─────────────────────────────────────────────────────────────────────────
# 6. 날짜 기반 분석 패턴
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "─" * 70)
print(" 6. 날짜 기반 분석 패턴")
print("─" * 70)

# 요일별 평균 매출
print("\n[요일별 평균 매출]")
weekday_sales = {i: [] for i in range(7)}
weekday_names = ['월', '화', '수', '목', '금', '토', '일']
for d, s in zip(daily_dates, daily_sales):
    dt = datetime.strptime(d, '%Y-%m-%d')
    weekday_sales[dt.weekday()].append(s)

for wd in range(7):
    avg = sum(weekday_sales[wd]) / len(weekday_sales[wd])
    bar = "█" * int(avg / 10000)
    print(f"  {weekday_names[wd]}요일: {avg:>10,.0f}원 {bar}")
# ── Pandas: df.groupby(df.index.day_name()).mean() ──

# 이동 평균 (7일)
print("\n[이동 평균] 1월 매출 7일 이동 평균:")
window = 7
for i in range(window - 1, min(31, len(daily_sales))):
    window_sales = daily_sales[i - window + 1:i + 1]
    moving_avg = sum(window_sales) / window
    date = daily_dates[i]
    bar = "▒" * int(moving_avg / 10000)
    print(f"  {date}: {moving_avg:>10,.0f}원 {bar}")
# ── Pandas: df['매출'].rolling(window=7).mean() ──


# ─────────────────────────────────────────────────────────────────────────
# ★ 실습: 출석부 날짜 데이터 분석
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" ★ 실습: 출석부 날짜 데이터 분석")
print("═" * 70)

# 출석 데이터 생성
students = ['김민수', '이영희', '박철수', '최지영', '정하늘']
attendance_dates = []
attendance_names = []
attendance_status = []

random.seed(123)
school_days = []
d = datetime(2024, 3, 4)
while d <= datetime(2024, 3, 29):
    if d.weekday() < 5:  # 평일만
        school_days.append(d)
    d += timedelta(days=1)

for day in school_days:
    for student in students:
        attendance_dates.append(day.strftime('%Y-%m-%d'))
        attendance_names.append(student)
        r = random.random()
        if r > 0.95:
            attendance_status.append('결석')
        elif r > 0.90:
            attendance_status.append('지각')
        elif r > 0.85:
            attendance_status.append('조퇴')
        else:
            attendance_status.append('출석')

print(f"\n  출석 데이터: {len(attendance_dates)}건")
print(f"  기간: {attendance_dates[0]} ~ {attendance_dates[-1]}")
print(f"  학생: {students}")

# 1. 학생별 출석 현황
print("\n── 1. 학생별 출석 현황 ──")
for student in students:
    counts = {'출석': 0, '지각': 0, '조퇴': 0, '결석': 0}
    for name, status in zip(attendance_names, attendance_status):
        if name == student:
            counts[status] += 1
    total = sum(counts.values())
    attend_rate = counts['출석'] / total * 100
    print(f"  {student}: 출석={counts['출석']}, 지각={counts['지각']}, "
          f"조퇴={counts['조퇴']}, 결석={counts['결석']} "
          f"(출석률: {attend_rate:.0f}%)")
# ── Pandas: pd.crosstab(df['이름'], df['상태']) ──

# 2. 요일별 결석률
print("\n── 2. 요일별 결석률 ──")
weekday_absent = {i: [0, 0] for i in range(5)}  # [결석수, 전체수]
for date, status in zip(attendance_dates, attendance_status):
    dt = datetime.strptime(date, '%Y-%m-%d')
    wd = dt.weekday()
    weekday_absent[wd][1] += 1
    if status == '결석':
        weekday_absent[wd][0] += 1

day_names_kor = ['월', '화', '수', '목', '금']
for wd in range(5):
    absent, total = weekday_absent[wd]
    rate = absent / total * 100 if total > 0 else 0
    bar = "█" * int(rate * 2) if rate > 0 else "·"
    print(f"  {day_names_kor[wd]}요일: {rate:.1f}% ({absent}/{total}) {bar}")

# 3. 주차별 출석률 추이
print("\n── 3. 주차별 출석률 추이 ──")
weekly_attend = {}
for date, status in zip(attendance_dates, attendance_status):
    dt = datetime.strptime(date, '%Y-%m-%d')
    week = f"W{dt.isocalendar()[1]}"
    if week not in weekly_attend:
        weekly_attend[week] = [0, 0]  # [출석, 전체]
    weekly_attend[week][1] += 1
    if status == '출석':
        weekly_attend[week][0] += 1

for week in sorted(weekly_attend.keys()):
    attend, total = weekly_attend[week]
    rate = attend / total * 100
    bar = "█" * int(rate / 5)
    print(f"  {week}: {'█' * int(rate/5)}{'░' * (20 - int(rate/5))} {rate:.0f}%")

# 4. 개근 학생 찾기
print("\n── 4. 3월 개근 학생 ──")
for student in students:
    has_absent = False
    for name, status in zip(attendance_names, attendance_status):
        if name == student and status == '결석':
            has_absent = True
            break
    print(f"  {student}: {'개근!' if not has_absent else '결석 있음'}")

# ── Pandas로 전체 분석: ──
# df['날짜'] = pd.to_datetime(df['날짜'])
# df.set_index('날짜', inplace=True)
#
# # 학생별 출석 현황
# pd.crosstab(df['이름'], df['상태'])
#
# # 요일별 결석률
# df['요일'] = df.index.day_name()
# df.groupby('요일')['상태'].apply(lambda x: (x == '결석').mean())
#
# # 주차별 출석률
# df.resample('W')['상태'].apply(lambda x: (x == '출석').mean())


# ─────────────────────────────────────────────────────────────────────────
# 정리
# ─────────────────────────────────────────────────────────────────────────

print("\n" + "═" * 70)
print(" 정리: 문자열 & 날짜 도구 모음")
print("═" * 70)

print("""
  ┌─ 문자열 (str 접근자) ─────────────────────────────┐
  │ df['열'].str.upper()         대문자 변환          │
  │ df['열'].str.lower()         소문자 변환          │
  │ df['열'].str.strip()         공백 제거            │
  │ df['열'].str.len()           길이                 │
  │ df['열'].str.contains('패턴') 포함 여부           │
  │ df['열'].str.startswith('x') 시작 문자            │
  │ df['열'].str.replace('a','b') 치환                │
  │ df['열'].str.split('구분자')  분리                │
  │ df['열'].str.extract(r'(패턴)') 정규식 추출       │
  │ df['열'].str[0]              인덱싱               │
  └────────────────────────────────────────────────────┘

  ┌─ 날짜/시간 (dt 접근자) ───────────────────────────┐
  │ pd.to_datetime(df['열'])    datetime 변환          │
  │ df['날짜'].dt.year          연도                   │
  │ df['날짜'].dt.month         월                     │
  │ df['날짜'].dt.day           일                     │
  │ df['날짜'].dt.day_name()    요일 이름              │
  │ df['날짜'].dt.quarter       분기                   │
  │ df['날짜'].dt.weekday       요일 번호 (0=월)       │
  │ pd.Timedelta(days=7)       시간 간격              │
  │ df.resample('M').sum()     월별 집계              │
  │ df['열'].rolling(7).mean() 이동 평균              │
  └────────────────────────────────────────────────────┘
""")

print("✅ 07단계 완료! 다음은 08_io_read_write.py에서 파일 입출력을 배워요!")
