# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 14단계: 데이터 분석 기초
#   ─ 데이터 구조, 정제, 필터링, 그룹화, 통계, 시각화, 변환, 실전 분석 ─
#   ■ 실행 방법: python 14_data_analysis.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. 데이터 분석이란? — 수집→정제→탐색→시각화→인사이트
#   2. 데이터 구조 설계 — 테이블형 데이터, 행 기반 vs 열 기반
#   3. 데이터 정제 — 결측값, 이상치, 중복 제거, 타입 변환
#   4. 필터링과 정렬 — 조건별 필터, 다중 조건, sorted
#   5. 그룹화와 집계 — groupby 구현, sum/avg/count/min/max, 피벗 테이블
#   6. 통계 함수 직접 구현 — mean, median, mode, std, 상관계수
#   7. 텍스트 데이터로 시각화 — ASCII 막대그래프, 히스토그램, 산점도
#   8. 데이터 변환 — map/apply, 파생 변수 생성, 범주화(binning)
#   9. 실전: 학교 급식 만족도 조사 데이터 분석
#
# ─────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import math
from collections import Counter, defaultdict


# =========================================================================
#
#   레슨 1 — 데이터 분석이란?
#
# =========================================================================

def lesson1_what_is_data_analysis():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : 데이터 분석이란?             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 데이터 분석이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   "많은 데이터에서 의미 있는 패턴을 찾아 결론을 내리는 과정"
    #
    #   비유: 탐정의 수사 과정
    #     1. 증거 수집 (데이터 수집)
    #     2. 증거 정리 (데이터 정제)
    #     3. 단서 분석 (데이터 탐색)
    #     4. 보고서 작성 (시각화/보고)
    #     5. 범인 지목 (인사이트 도출)
    #

    print("  ■ 데이터 분석 5단계 프로세스:")
    print()
    print("    ┌─────────┐    ┌─────────┐    ┌─────────┐")
    print("    │ 1. 수집  │ →  │ 2. 정제  │ →  │ 3. 탐색  │")
    print("    └─────────┘    └─────────┘    └─────────┘")
    print("                                       │")
    print("    ┌─────────┐    ┌─────────┐         ↓")
    print("    │5. 인사이트│ ← │ 4. 시각화 │ ← ──────┘")
    print("    └─────────┘    └─────────┘")
    print()

    steps = [
        ("1. 수집", "데이터를 모으는 단계", "설문조사, 로그, API, 파일"),
        ("2. 정제", "지저분한 데이터를 깨끗하게", "결측값, 이상치, 중복 처리"),
        ("3. 탐색", "데이터의 특성을 파악", "통계, 분포, 상관관계"),
        ("4. 시각화", "눈에 보이게 그래프로", "막대, 선, 산점도, 히스토그램"),
        ("5. 인사이트", "의미 있는 결론 도출", "패턴, 추세, 이상 발견"),
    ]

    for step, desc, example in steps:
        print(f"    {step}: {desc}")
        print(f"      예: {example}")
    print()

    # ─── 간단한 분석 맛보기 ───

    print("  ─── 간단한 분석 맛보기 ───")

    daily_sales = [15, 22, 18, 30, 25, 12, 35, 28, 20, 32]

    total = sum(daily_sales)
    avg = total / len(daily_sales)
    max_val = max(daily_sales)
    min_val = min(daily_sales)

    print(f"    10일간 판매량: {daily_sales}")
    print(f"    총 판매: {total}개")
    print(f"    평균: {avg:.1f}개/일")
    print(f"    최대: {max_val}개 (일일), 최소: {min_val}개 (일일)")
    print(f"    → 평균 대비 변동이 큼 → 원인 분석 필요!")
    print()


# =========================================================================
#
#   레슨 2 — 데이터 구조 설계
#
# =========================================================================

def lesson2_data_structure():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 데이터 구조 설계             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 테이블형 데이터
    # ─────────────────────────────────────────────────────────────────────
    #
    #   데이터 분석에서 가장 흔한 구조: 행(row)과 열(column)의 표!
    #
    #   엑셀 스프레드시트를 떠올리면 됩니다.
    #     행 = 하나의 데이터 레코드 (학생 1명)
    #     열 = 하나의 속성 (이름, 나이, 점수)
    #

    # ─── 행 기반 (Row-based) — 가장 직관적 ───

    print("  ■ 행 기반 데이터 (list of dicts):")

    students_rows = [
        {"name": "민수", "grade": 3, "math": 95, "science": 88},
        {"name": "지유", "grade": 4, "math": 100, "science": 92},
        {"name": "서연", "grade": 3, "math": 78, "science": 85},
        {"name": "하준", "grade": 5, "math": 82, "science": 90},
    ]

    for s in students_rows:
        print(f"    {s}")
    print()
    print("    장점: 한 레코드의 모든 정보를 한 번에 볼 수 있음")
    print("    단점: 특정 열만 꺼내려면 반복문 필요")
    print()

    # ─── 열 기반 (Column-based) — 분석에 유리 ───

    print("  ■ 열 기반 데이터 (dict of lists):")

    students_cols = {
        "name": ["민수", "지유", "서연", "하준"],
        "grade": [3, 4, 3, 5],
        "math": [95, 100, 78, 82],
        "science": [88, 92, 85, 90],
    }

    for col, values in students_cols.items():
        print(f"    {col}: {values}")
    print()
    print("    장점: 열 단위 연산 빠름 (평균, 합계 등)")
    print("    단점: 한 레코드를 보려면 여러 열을 조합해야 함")
    print()

    # ─── 변환 함수 ───

    print("  ─── 행 ↔ 열 변환 ───")

    def rows_to_cols(rows: list[dict]) -> dict[str, list]:
        """행 기반 → 열 기반 변환."""
        if not rows:
            return {}
        cols = {key: [] for key in rows[0]}
        for row in rows:
            for key in cols:
                cols[key].append(row.get(key))
        return cols

    def cols_to_rows(cols: dict[str, list]) -> list[dict]:
        """열 기반 → 행 기반 변환."""
        if not cols:
            return []
        keys = list(cols.keys())
        num_rows = len(cols[keys[0]])
        return [{key: cols[key][i] for key in keys} for i in range(num_rows)]

    converted_cols = rows_to_cols(students_rows)
    converted_rows = cols_to_rows(students_cols)

    print(f"    행→열 변환: math 열 = {converted_cols['math']}")
    print(f"    열→행 변환: 첫 번째 행 = {converted_rows[0]}")
    print()


# =========================================================================
#
#   레슨 3 — 데이터 정제
#
# =========================================================================

def lesson3_data_cleaning():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 데이터 정제                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 데이터 정제란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   현실의 데이터는 항상 지저분합니다!
    #
    #   비유: 요리 전 재료 손질
    #     → 흙 묻은 당근을 씻고, 썩은 부분 잘라내고, 크기 맞추기
    #     → 재료 손질 없이 요리하면? 맛없음!
    #     → 데이터 정제 없이 분석하면? 잘못된 결론!
    #

    # ─── 지저분한 데이터 ───

    raw_data = [
        {"name": "민수", "age": "15", "score": "95", "class": "A"},
        {"name": "지유", "age": "16", "score": "", "class": "B"},         # 결측값!
        {"name": " 서연 ", "age": "14", "score": "78", "class": "A"},     # 공백!
        {"name": "하준", "age": "200", "score": "82", "class": "A"},      # 이상치!
        {"name": "민수", "age": "15", "score": "95", "class": "A"},       # 중복!
        {"name": "도윤", "age": "15", "score": "-10", "class": "C"},      # 이상치!
        {"name": "유나", "age": "abc", "score": "88", "class": "B"},      # 잘못된 타입!
    ]

    print("  ─── 원본 데이터 (문제 투성이!) ───")
    for i, row in enumerate(raw_data):
        print(f"    {i}: {row}")
    print()

    # ─── 1. 타입 변환 ───

    print("  ■ 1단계: 타입 변환")

    def safe_int(value, default=None):
        """안전한 정수 변환. 실패하면 default 반환."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    cleaned = []
    for row in raw_data:
        cleaned.append({
            "name": row["name"].strip(),
            "age": safe_int(row["age"]),
            "score": safe_int(row["score"]),
            "class": row["class"],
        })

    print(f"    'abc' → {safe_int('abc')} (None)")
    print(f"    '' → {safe_int('')} (None)")
    print(f"    '95' → {safe_int('95')}")
    print()

    # ─── 2. 결측값 처리 ───

    print("  ■ 2단계: 결측값 처리")

    valid_scores = [r["score"] for r in cleaned if r["score"] is not None]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    for row in cleaned:
        if row["score"] is None:
            row["score"] = int(avg_score)
            print(f"    {row['name']}: 결측값 → 평균({int(avg_score)})으로 대체")
        if row["age"] is None:
            row["age"] = 0  # 나이는 0으로 마킹 (제외 대상)
            print(f"    {row['name']}: 나이 변환 실패 → 0으로 마킹")
    print()

    # ─── 3. 이상치 탐지 ───

    print("  ■ 3단계: 이상치 탐지 및 제거")

    def detect_outliers(data: list[dict], field: str,
                        min_val: int, max_val: int) -> list[dict]:
        """범위를 벗어나는 이상치를 찾습니다."""
        outliers = []
        for row in data:
            val = row.get(field)
            if val is not None and (val < min_val or val > max_val):
                outliers.append(row)
        return outliers

    age_outliers = detect_outliers(cleaned, "age", 10, 20)
    score_outliers = detect_outliers(cleaned, "score", 0, 100)

    for o in age_outliers:
        print(f"    나이 이상치: {o['name']} (age={o['age']})")
    for o in score_outliers:
        print(f"    점수 이상치: {o['name']} (score={o['score']})")

    # 이상치 제거
    cleaned = [r for r in cleaned
               if 10 <= (r["age"] or 0) <= 20 and 0 <= (r["score"] or 0) <= 100]
    print(f"    이상치 제거 후: {len(cleaned)}건")
    print()

    # ─── 4. 중복 제거 ───

    print("  ■ 4단계: 중복 제거")

    seen = set()
    unique = []
    for row in cleaned:
        key = (row["name"], row["age"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
        else:
            print(f"    중복 제거: {row['name']}")

    print(f"    중복 제거 후: {len(unique)}건")
    print()

    # ─── 정제 결과 ───

    print("  ─── 정제 완료 데이터 ───")
    for row in unique:
        print(f"    {row}")
    print()


# =========================================================================
#
#   레슨 4 — 필터링과 정렬
#
# =========================================================================

def lesson4_filter_sort():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 필터링과 정렬               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 필터링 = 원하는 데이터만 골라내기
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 체로 쌀 거르기 — 돌멩이와 벌레를 걸러내고 쌀만 남기기!
    #

    data = [
        {"name": "민수", "grade": 3, "math": 95, "eng": 88, "class": "A"},
        {"name": "지유", "grade": 4, "math": 100, "eng": 92, "class": "B"},
        {"name": "서연", "grade": 3, "math": 78, "eng": 85, "class": "A"},
        {"name": "하준", "grade": 5, "math": 82, "eng": 90, "class": "A"},
        {"name": "도윤", "grade": 4, "math": 65, "eng": 70, "class": "C"},
        {"name": "유나", "grade": 3, "math": 90, "eng": 95, "class": "B"},
    ]

    # ─── 단일 조건 필터 ───

    print("  ─── 단일 조건 필터 ───")
    grade3 = [s for s in data if s["grade"] == 3]
    print(f"    3학년: {[s['name'] for s in grade3]}")

    math_90_plus = [s for s in data if s["math"] >= 90]
    print(f"    수학 90점 이상: {[s['name'] for s in math_90_plus]}")
    print()

    # ─── 다중 조건 필터 ───

    print("  ─── 다중 조건 필터 ───")

    # AND 조건
    grade3_math90 = [s for s in data if s["grade"] == 3 and s["math"] >= 90]
    print(f"    3학년 AND 수학90+: {[s['name'] for s in grade3_math90]}")

    # OR 조건
    a_or_b_class = [s for s in data if s["class"] in ("A", "B")]
    print(f"    A반 OR B반: {[s['name'] for s in a_or_b_class]}")

    # 평균 기반 필터
    high_avg = [s for s in data if (s["math"] + s["eng"]) / 2 >= 85]
    print(f"    평균 85+: {[s['name'] for s in high_avg]}")
    print()

    # ─── 필터 함수 만들기 ───

    print("  ─── 동적 필터 함수 ───")

    def filter_data(data: list[dict], **conditions) -> list[dict]:
        """키워드 인자로 필터 조건을 전달합니다."""
        result = data
        for field, value in conditions.items():
            if field.endswith("__gte"):  # greater than or equal
                key = field[:-5]
                result = [r for r in result if r.get(key, 0) >= value]
            elif field.endswith("__lte"):  # less than or equal
                key = field[:-5]
                result = [r for r in result if r.get(key, 0) <= value]
            elif field.endswith("__in"):  # in list
                key = field[:-4]
                result = [r for r in result if r.get(key) in value]
            else:
                result = [r for r in result if r.get(field) == value]
        return result

    r = filter_data(data, grade=3, math__gte=80)
    print(f"    grade=3, math>=80: {[s['name'] for s in r]}")
    r = filter_data(data, class__in=["A", "B"], eng__gte=90)
    print(f"    class in [A,B], eng>=90: {[s['name'] for s in r]}")
    print()

    # ─── 정렬 ───

    print("  ─── 정렬 ───")

    # 단일 키 정렬
    by_math = sorted(data, key=lambda s: s["math"], reverse=True)
    print(f"    수학 점수 내림차순: {[(s['name'], s['math']) for s in by_math]}")

    # 복합 정렬 (학년 오름차순, 수학 내림차순)
    by_grade_math = sorted(data, key=lambda s: (s["grade"], -s["math"]))
    print(f"    학년↑ → 수학↓:")
    for s in by_grade_math:
        print(f"      {s['grade']}학년 {s['name']}: 수학 {s['math']}")
    print()


# =========================================================================
#
#   레슨 5 — 그룹화와 집계
#
# =========================================================================

def lesson5_groupby():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : 그룹화와 집계               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 그룹화(GroupBy)란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   같은 범주끼리 묶어서 요약 통계를 내는 것입니다.
    #
    #   비유: 체육대회 반별 점수 집계
    #     → 각 반의 학생 점수를 모아서 합계, 평균 계산!
    #

    sales = [
        {"product": "연필", "region": "서울", "qty": 100, "price": 500},
        {"product": "공책", "region": "부산", "qty": 50, "price": 1500},
        {"product": "연필", "region": "부산", "qty": 80, "price": 500},
        {"product": "지우개", "region": "서울", "qty": 200, "price": 300},
        {"product": "공책", "region": "서울", "qty": 70, "price": 1500},
        {"product": "연필", "region": "대구", "qty": 60, "price": 500},
        {"product": "지우개", "region": "부산", "qty": 150, "price": 300},
        {"product": "공책", "region": "대구", "qty": 30, "price": 1500},
    ]

    # ─── groupby 함수 구현 ───

    def groupby(data: list[dict], key: str) -> dict[str, list[dict]]:
        """지정한 키로 데이터를 그룹화합니다."""
        groups = defaultdict(list)
        for row in data:
            groups[row[key]].append(row)
        return dict(groups)

    def agg(groups: dict, field: str, func: str) -> dict:
        """그룹별 집계를 수행합니다."""
        result = {}
        for group_key, rows in groups.items():
            values = [r[field] for r in rows]
            if func == "sum":
                result[group_key] = sum(values)
            elif func == "avg":
                result[group_key] = sum(values) / len(values)
            elif func == "count":
                result[group_key] = len(values)
            elif func == "min":
                result[group_key] = min(values)
            elif func == "max":
                result[group_key] = max(values)
        return result

    # ─── 상품별 그룹화 ───

    print("  ─── 상품별 집계 ───")
    by_product = groupby(sales, "product")

    qty_sum = agg(by_product, "qty", "sum")
    print(f"    판매 수량 합계: {qty_sum}")

    # 매출액 계산 (qty * price)
    revenue_by_product = {}
    for product, rows in by_product.items():
        revenue_by_product[product] = sum(r["qty"] * r["price"] for r in rows)
    print(f"    매출액: {revenue_by_product}")
    print()

    # ─── 지역별 그룹화 ───

    print("  ─── 지역별 집계 ───")
    by_region = groupby(sales, "region")

    for region, rows in by_region.items():
        total_revenue = sum(r["qty"] * r["price"] for r in rows)
        count = len(rows)
        print(f"    {region}: {count}건, 매출 {total_revenue:,}원")
    print()

    # ─── 피벗 테이블 개념 ───

    print("  ─── 피벗 테이블 (상품 × 지역 → 수량) ───")

    def pivot_table(data, row_key, col_key, value_key, agg_func="sum"):
        """피벗 테이블을 만듭니다."""
        table = defaultdict(lambda: defaultdict(list))
        cols = set()
        for row in data:
            r = row[row_key]
            c = row[col_key]
            table[r][c].append(row[value_key])
            cols.add(c)

        cols = sorted(cols)
        result = {}
        for r, col_data in table.items():
            result[r] = {}
            for c in cols:
                values = col_data.get(c, [0])
                if agg_func == "sum":
                    result[r][c] = sum(values)
                elif agg_func == "avg":
                    result[r][c] = sum(values) / len(values) if values else 0
        return result, cols

    pivot, columns = pivot_table(sales, "product", "region", "qty")

    # 피벗 테이블 출력
    print(f"    {'상품':<8}", end="")
    for col in columns:
        print(f" {col:>6}", end="")
    print(f" {'합계':>6}")

    print(f"    {'─' * 8}", end="")
    for _ in columns:
        print(f" {'─' * 6}", end="")
    print(f" {'─' * 6}")

    for product, vals in pivot.items():
        print(f"    {product:<8}", end="")
        row_total = 0
        for col in columns:
            v = vals.get(col, 0)
            row_total += v
            print(f" {v:>6}", end="")
        print(f" {row_total:>6}")
    print()


# =========================================================================
#
#   레슨 6 — 통계 함수 직접 구현
#
# =========================================================================

def lesson6_statistics():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 통계 함수 직접 구현          │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 기본 통계 개념
    # ─────────────────────────────────────────────────────────────────────
    #
    #   비유: 학급 시험 점수 분석
    #     → "전체적으로 어떤가?" → 평균
    #     → "중간은 얼마인가?" → 중앙값
    #     → "가장 많은 점수는?" → 최빈값
    #     → "얼마나 흩어져 있나?" → 표준편차
    #

    scores = [78, 85, 92, 65, 88, 95, 72, 90, 85, 80, 88, 76, 85, 93, 70]

    # ─── 평균 (Mean) ───

    def mean(data: list[float]) -> float:
        """산술 평균을 계산합니다."""
        return sum(data) / len(data)

    avg = mean(scores)
    print(f"  ■ 평균 (Mean): {avg:.2f}")
    print(f"    공식: 모든 값의 합 / 개수 = {sum(scores)} / {len(scores)}")
    print()

    # ─── 중앙값 (Median) ───

    def median(data: list[float]) -> float:
        """중앙값을 계산합니다."""
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        return sorted_data[mid]

    med = median(scores)
    print(f"  ■ 중앙값 (Median): {med}")
    print(f"    정렬: {sorted(scores)}")
    print(f"    → 가운데 값!")
    print(f"    → 평균과 다를 수 있음 (극단값에 영향 안 받음)")
    print()

    # ─── 최빈값 (Mode) ───

    def mode(data: list) -> list:
        """최빈값을 계산합니다. 여러 개일 수 있음."""
        counter = Counter(data)
        max_count = max(counter.values())
        return [val for val, count in counter.items() if count == max_count]

    mod = mode(scores)
    print(f"  ■ 최빈값 (Mode): {mod}")
    print(f"    빈도: {dict(Counter(scores))}")
    print()

    # ─── 분산과 표준편차 ───

    def variance(data: list[float], sample: bool = True) -> float:
        """분산을 계산합니다. sample=True이면 표본분산(n-1)."""
        avg = mean(data)
        sq_diff = [(x - avg) ** 2 for x in data]
        n = len(data) - 1 if sample else len(data)
        return sum(sq_diff) / n

    def std_dev(data: list[float], sample: bool = True) -> float:
        """표준편차를 계산합니다."""
        return math.sqrt(variance(data, sample))

    var = variance(scores)
    std = std_dev(scores)
    print(f"  ■ 분산 (Variance): {var:.2f}")
    print(f"  ■ 표준편차 (Std Dev): {std:.2f}")
    print(f"    → 표준편차가 클수록 데이터가 넓게 퍼져 있음")
    print(f"    → 평균 ± 1σ ({avg - std:.1f} ~ {avg + std:.1f})에 약 68%가 있음")
    print()

    # ─── 상관계수 (Correlation) ───

    def correlation(x: list[float], y: list[float]) -> float:
        """피어슨 상관계수를 계산합니다 (-1 ~ 1)."""
        n = len(x)
        mean_x = mean(x)
        mean_y = mean(y)

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

        if denom_x == 0 or denom_y == 0:
            return 0
        return numerator / (denom_x * denom_y)

    math_scores = [95, 85, 78, 92, 88, 65, 90, 72]
    science_scores = [90, 82, 75, 88, 85, 60, 87, 70]

    corr = correlation(math_scores, science_scores)
    print(f"  ■ 상관계수 (수학 vs 과학): {corr:.4f}")
    print(f"    → 1에 가까울수록 양의 상관 (같이 올라감)")
    print(f"    → -1에 가까울수록 음의 상관 (반대로)")
    print(f"    → 0에 가까울수록 관계 없음")
    print()


# =========================================================================
#
#   레슨 7 — 텍스트 데이터로 시각화
#
# =========================================================================

def lesson7_ascii_visualization():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 텍스트 시각화               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 왜 텍스트 시각화?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   matplotlib 없이도 터미널에서 데이터를 시각적으로 표현할 수 있습니다!
    #   로그 분석, SSH 접속 환경, 간단한 대시보드에 유용합니다.
    #

    # ─── 수평 막대 그래프 ───

    print("  ─── 수평 막대 그래프 ───")

    def bar_chart_h(data: dict[str, float], max_width: int = 30, symbol: str = "█"):
        """수평 막대 그래프를 출력합니다."""
        max_val = max(data.values()) if data else 1
        for label, value in data.items():
            bar_len = int(value / max_val * max_width)
            bar = symbol * bar_len
            print(f"    {label:>8} | {bar} {value}")

    sales = {"연필": 250, "공책": 180, "지우개": 320, "볼펜": 150, "자": 90}
    bar_chart_h(sales)
    print()

    # ─── 수직 막대 그래프 ───

    print("  ─── 수직 막대 그래프 ───")

    def bar_chart_v(data: dict[str, float], height: int = 10):
        """수직 막대 그래프를 출력합니다."""
        max_val = max(data.values()) if data else 1
        labels = list(data.keys())
        values = list(data.values())

        for row in range(height, 0, -1):
            threshold = max_val * row / height
            line = "    "
            for val in values:
                if val >= threshold:
                    line += " ██"
                else:
                    line += "   "
            print(line)

        print("    " + "───" * len(labels))
        line = "    "
        for label in labels:
            line += f" {label[:2]:>2}"
        print(line)

    monthly_sales = {"1월": 80, "2월": 60, "3월": 95, "4월": 70, "5월": 110, "6월": 85}
    bar_chart_v(monthly_sales, height=8)
    print()

    # ─── 히스토그램 ───

    print("  ─── 히스토그램 (점수 분포) ───")

    def histogram(data: list[float], bins: int = 5, width: int = 25):
        """히스토그램을 출력합니다."""
        min_val = min(data)
        max_val = max(data)
        bin_size = (max_val - min_val) / bins

        bin_counts = [0] * bins
        for val in data:
            idx = min(int((val - min_val) / bin_size), bins - 1)
            bin_counts[idx] += 1

        max_count = max(bin_counts) if bin_counts else 1

        for i in range(bins):
            lo = min_val + i * bin_size
            hi = lo + bin_size
            bar_len = int(bin_counts[i] / max_count * width)
            bar = "█" * bar_len
            print(f"    {lo:5.0f}-{hi:5.0f} | {bar} ({bin_counts[i]})")

    scores = [65, 72, 78, 80, 82, 85, 85, 85, 88, 88, 90, 92, 93, 95, 78, 70, 76]
    histogram(scores, bins=6)
    print()

    # ─── 간단한 산점도 ───

    print("  ─── 산점도 (수학 vs 과학) ───")

    def scatter_plot(x_data: list[float], y_data: list[float],
                     width: int = 30, height: int = 12):
        """간단한 ASCII 산점도를 출력합니다."""
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)

        # 그리드 초기화
        grid = [[" "] * width for _ in range(height)]

        # 점 찍기
        for x, y in zip(x_data, y_data):
            col = int((x - x_min) / (x_max - x_min + 1e-9) * (width - 1))
            row = height - 1 - int((y - y_min) / (y_max - y_min + 1e-9) * (height - 1))
            grid[row][col] = "●"

        # 출력
        for i, row in enumerate(grid):
            if i == 0:
                y_label = f"{y_max:.0f}"
            elif i == height - 1:
                y_label = f"{y_min:.0f}"
            else:
                y_label = ""
            print(f"    {y_label:>4} │{''.join(row)}")
        print(f"         └{'─' * width}")
        print(f"         {x_min:.0f}{' ' * (width - 6)}{x_max:.0f}")

    math_s = [95, 85, 78, 92, 88, 65, 90, 72, 80, 85]
    science_s = [90, 82, 75, 88, 85, 60, 87, 70, 78, 83]
    scatter_plot(math_s, science_s)
    print()


# =========================================================================
#
#   레슨 8 — 데이터 변환
#
# =========================================================================

def lesson8_data_transform():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 데이터 변환                 │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 데이터 변환이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   원본 데이터를 분석에 적합한 형태로 바꾸는 것입니다.
    #
    #   비유: 요리 재료를 다듬는 것
    #     → 당근을 채 썰기, 감자를 깍둑썰기
    #     → 같은 재료도 어떻게 자르느냐에 따라 요리가 달라짐!
    #

    data = [
        {"name": "민수", "birth_year": 2010, "score": 95},
        {"name": "지유", "birth_year": 2009, "score": 88},
        {"name": "서연", "birth_year": 2010, "score": 72},
        {"name": "하준", "birth_year": 2008, "score": 85},
        {"name": "도윤", "birth_year": 2011, "score": 60},
        {"name": "유나", "birth_year": 2009, "score": 92},
    ]

    # ─── map/apply 개념 ───

    print("  ─── map 함수 활용 ───")

    def map_field(data: list[dict], field: str, func) -> list[dict]:
        """특정 필드에 함수를 적용합니다."""
        result = []
        for row in data:
            new_row = dict(row)
            new_row[field] = func(row[field])
            result.append(new_row)
        return result

    # 점수를 100점 만점 → 5점 만점으로 변환
    scaled = map_field(data, "score", lambda s: round(s / 20, 1))
    print("    점수 스케일 변환 (100→5점):")
    for s in scaled:
        print(f"      {s['name']}: {s['score']}")
    print()

    # ─── 파생 변수 생성 ───

    print("  ─── 파생 변수 생성 ───")

    current_year = 2026

    def add_derived(data: list[dict]) -> list[dict]:
        """원본 데이터에 파생 변수를 추가합니다."""
        result = []
        for row in data:
            new_row = dict(row)
            # 나이 계산
            new_row["age"] = current_year - row["birth_year"]
            # 합격 여부
            new_row["passed"] = row["score"] >= 70
            # 등급
            s = row["score"]
            if s >= 90:
                new_row["grade"] = "A"
            elif s >= 80:
                new_row["grade"] = "B"
            elif s >= 70:
                new_row["grade"] = "C"
            else:
                new_row["grade"] = "F"
            result.append(new_row)
        return result

    enriched = add_derived(data)
    print(f"    {'이름':^6} {'나이':>4} {'점수':>5} {'등급':^4} {'합격':^4}")
    print(f"    {'─' * 6} {'─' * 4} {'─' * 5} {'─' * 4} {'─' * 4}")
    for r in enriched:
        passed_str = "O" if r["passed"] else "X"
        print(f"    {r['name']:^6} {r['age']:>4} {r['score']:>5} {r['grade']:^4} {passed_str:^4}")
    print()

    # ─── 범주화 (Binning) ───

    print("  ─── 범주화 (Binning) ───")

    def categorize(value: float, bins: list[tuple[float, float, str]]) -> str:
        """값을 범주로 변환합니다."""
        for lo, hi, label in bins:
            if lo <= value < hi:
                return label
        return "기타"

    score_bins = [
        (0, 60, "매우 낮음"),
        (60, 70, "낮음"),
        (70, 80, "보통"),
        (80, 90, "높음"),
        (90, 101, "매우 높음"),
    ]

    print("    점수 범주화:")
    for row in data:
        category = categorize(row["score"], score_bins)
        print(f"      {row['name']}: {row['score']}점 → {category}")
    print()

    # ─── 정규화 (Normalization) ───

    print("  ─── 정규화 (0~1 범위) ───")

    scores = [r["score"] for r in data]
    min_s, max_s = min(scores), max(scores)

    print("    정규화 공식: (값 - 최소) / (최대 - 최소)")
    for row in data:
        normalized = (row["score"] - min_s) / (max_s - min_s)
        print(f"      {row['name']}: {row['score']} → {normalized:.3f}")
    print()


# =========================================================================
#
#   레슨 9 — 실전: 학교 급식 만족도 조사 데이터 분석
#
# =========================================================================

def lesson9_lunch_survey():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 급식 만족도 데이터 분석       │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 시나리오
    # ─────────────────────────────────────────────────────────────────────
    #
    #   학교에서 급식 만족도 설문조사를 했습니다.
    #   데이터를 분석하여 인사이트를 도출합니다.
    #
    #   조사 항목:
    #   - 학년 (3~6학년)
    #   - 급식 메뉴 (한식/양식/중식/분식)
    #   - 맛 점수 (1~5점)
    #   - 양 점수 (1~5점)
    #   - 재주문 의향 (Y/N)
    #

    survey_data = [
        {"grade": 3, "menu": "한식", "taste": 4, "portion": 3, "reorder": "Y"},
        {"grade": 3, "menu": "양식", "taste": 5, "portion": 4, "reorder": "Y"},
        {"grade": 3, "menu": "중식", "taste": 3, "portion": 4, "reorder": "N"},
        {"grade": 4, "menu": "한식", "taste": 4, "portion": 4, "reorder": "Y"},
        {"grade": 4, "menu": "양식", "taste": 5, "portion": 5, "reorder": "Y"},
        {"grade": 4, "menu": "분식", "taste": 4, "portion": 3, "reorder": "Y"},
        {"grade": 4, "menu": "중식", "taste": 2, "portion": 3, "reorder": "N"},
        {"grade": 5, "menu": "한식", "taste": 3, "portion": 2, "reorder": "N"},
        {"grade": 5, "menu": "양식", "taste": 4, "portion": 4, "reorder": "Y"},
        {"grade": 5, "menu": "분식", "taste": 5, "portion": 5, "reorder": "Y"},
        {"grade": 5, "menu": "한식", "taste": 4, "portion": 3, "reorder": "Y"},
        {"grade": 5, "menu": "중식", "taste": 3, "portion": 3, "reorder": "N"},
        {"grade": 6, "menu": "양식", "taste": 5, "portion": 4, "reorder": "Y"},
        {"grade": 6, "menu": "한식", "taste": 3, "portion": 3, "reorder": "N"},
        {"grade": 6, "menu": "분식", "taste": 4, "portion": 4, "reorder": "Y"},
        {"grade": 6, "menu": "중식", "taste": 2, "portion": 2, "reorder": "N"},
        {"grade": 3, "menu": "분식", "taste": 5, "portion": 4, "reorder": "Y"},
        {"grade": 4, "menu": "한식", "taste": 3, "portion": 3, "reorder": "N"},
        {"grade": 5, "menu": "양식", "taste": 5, "portion": 5, "reorder": "Y"},
        {"grade": 6, "menu": "분식", "taste": 4, "portion": 3, "reorder": "Y"},
    ]

    print(f"  총 응답 수: {len(survey_data)}건")
    print()

    # ─── 분석 1: 메뉴별 맛 평균 ───

    print("  ═══════════════════════════════════════")
    print("  분석 1: 메뉴별 맛 점수 평균")
    print("  ═══════════════════════════════════════")

    by_menu = defaultdict(list)
    for row in survey_data:
        by_menu[row["menu"]].append(row["taste"])

    menu_avg = {}
    for menu, scores in sorted(by_menu.items()):
        avg = sum(scores) / len(scores)
        menu_avg[menu] = avg

    max_avg = max(menu_avg.values())
    for menu, avg in sorted(menu_avg.items(), key=lambda x: -x[1]):
        bar_len = int(avg / 5 * 20)
        bar = "█" * bar_len
        star = " ★ 1위!" if avg == max_avg else ""
        print(f"    {menu:<4} {bar} {avg:.2f}점{star}")
    print()

    # ─── 분석 2: 학년별 만족도 ───

    print("  ═══════════════════════════════════════")
    print("  분석 2: 학년별 종합 만족도 (맛+양)")
    print("  ═══════════════════════════════════════")

    by_grade = defaultdict(list)
    for row in survey_data:
        combined = (row["taste"] + row["portion"]) / 2
        by_grade[row["grade"]].append(combined)

    for grade in sorted(by_grade):
        scores = by_grade[grade]
        avg = sum(scores) / len(scores)
        bar_len = int(avg / 5 * 20)
        bar = "█" * bar_len
        print(f"    {grade}학년 {bar} {avg:.2f}점 (응답 {len(scores)}건)")
    print()

    # ─── 분석 3: 재주문 의향 분석 ───

    print("  ═══════════════════════════════════════")
    print("  분석 3: 메뉴별 재주문 의향")
    print("  ═══════════════════════════════════════")

    reorder_by_menu = defaultdict(lambda: {"Y": 0, "N": 0})
    for row in survey_data:
        reorder_by_menu[row["menu"]][row["reorder"]] += 1

    for menu in sorted(reorder_by_menu):
        counts = reorder_by_menu[menu]
        total = counts["Y"] + counts["N"]
        rate = counts["Y"] / total * 100
        yes_bar = "●" * counts["Y"]
        no_bar = "○" * counts["N"]
        print(f"    {menu:<4} {yes_bar}{no_bar}  재주문 {rate:.0f}% ({counts['Y']}/{total})")
    print()

    # ─── 분석 4: 상관관계 (맛 점수 vs 재주문) ───

    print("  ═══════════════════════════════════════")
    print("  분석 4: 맛 점수 vs 재주문 의향")
    print("  ═══════════════════════════════════════")

    taste_reorder = defaultdict(lambda: {"Y": 0, "N": 0})
    for row in survey_data:
        taste_reorder[row["taste"]][row["reorder"]] += 1

    for taste in sorted(taste_reorder):
        counts = taste_reorder[taste]
        total = counts["Y"] + counts["N"]
        rate = counts["Y"] / total * 100
        print(f"    맛 {taste}점: 재주문율 {rate:5.1f}%  (Y:{counts['Y']}, N:{counts['N']})")
    print()

    # ─── 종합 인사이트 ───

    print("  ═══════════════════════════════════════")
    print("  종합 인사이트")
    print("  ═══════════════════════════════════════")
    print()

    # 맛 1위 메뉴
    best_menu = max(menu_avg, key=menu_avg.get)
    worst_menu = min(menu_avg, key=menu_avg.get)

    # 재주문율 1위 메뉴
    reorder_rates = {}
    for menu, counts in reorder_by_menu.items():
        total = counts["Y"] + counts["N"]
        reorder_rates[menu] = counts["Y"] / total * 100
    best_reorder = max(reorder_rates, key=reorder_rates.get)

    print(f"    1. 가장 맛있는 메뉴: {best_menu} ({menu_avg[best_menu]:.2f}점)")
    print(f"    2. 가장 아쉬운 메뉴: {worst_menu} ({menu_avg[worst_menu]:.2f}점)")
    print(f"    3. 재주문 의향 1위: {best_reorder} ({reorder_rates[best_reorder]:.0f}%)")
    print(f"    4. 맛 점수가 높을수록 재주문율 증가 (양의 상관)")
    print()
    print("    ★ 제안사항:")
    print(f"      → {best_menu}을 더 자주 편성하면 만족도 향상!")
    print(f"      → {worst_menu}의 레시피 개선 또는 빈도 축소 검토")
    print(f"      → 고학년의 '양' 점수가 낮으니 양 조절 필요")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 14단계: 데이터 분석 기초")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print()

    lesson1_what_is_data_analysis()
    lesson2_data_structure()
    lesson3_data_cleaning()
    lesson4_filter_sort()
    lesson5_groupby()
    lesson6_statistics()
    lesson7_ascii_visualization()
    lesson8_data_transform()
    lesson9_lunch_survey()

    print("=" * 60)
    print("  14단계 완료! 데이터 분석의 기초를 모두 배웠습니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()
