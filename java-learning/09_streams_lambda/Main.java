/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 09단계: 스트림과 람다
  ─ 람다식, 함수형 인터페이스, Stream API, map/filter/reduce ─

  [학습 목표]
  1. 람다식의 개념과 문법을 안다
  2. 함수형 인터페이스를 이해한다 (Predicate, Function, Consumer 등)
  3. Stream API의 기본 연산을 사용할 수 있다
  4. map, filter, reduce 패턴을 익힌다
  5. collect()로 결과를 수집할 수 있다
  6. Optional을 이해한다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.*;
import java.util.stream.*;
import java.util.function.*;


// =====================================================================
// 레슨 1 — 람다식 기초
// =====================================================================
/*
★ 람다식 = "이름 없는 짧은 함수"
  → 메서드를 하나의 식(expression)으로 표현한 것

  ┌──────────────────────────────────────────────┐
  │  비유: 람다는 "메모지에 적은 간단한 지시"      │
  │                                              │
  │  전통 방식: "김사원에게 문서 작성 지시서를     │
  │             작성하여 전달한다" (길다!)         │
  │                                              │
  │  람다 방식: "이거 해줘" ← 포스트잇 한 장!    │
  └──────────────────────────────────────────────┘

★ 람다 문법
  ┌───────────────────────────────────────────────┐
  │ (매개변수) -> { 본문 }                        │
  │                                               │
  │ (a, b) -> { return a + b; }   ← 기본 형태    │
  │ (a, b) -> a + b               ← 한 줄이면 중괄호+return 생략 │
  │ a -> a * 2                    ← 매개변수 1개면 괄호 생략     │
  │ () -> "hello"                 ← 매개변수 없으면 빈 괄호     │
  └───────────────────────────────────────────────┘

★ 람다 이전 vs 이후
  // 이전: 익명 내부 클래스
  Comparator<String> comp = new Comparator<String>() {
      @Override
      public int compare(String a, String b) {
          return a.length() - b.length();
      }
  };

  // 이후: 람다
  Comparator<String> comp = (a, b) -> a.length() - b.length();
*/


// =====================================================================
// 레슨 2 — 함수형 인터페이스
// =====================================================================
/*
★ 함수형 인터페이스 = 추상 메서드가 딱 1개인 인터페이스
  → 람다식으로 표현할 수 있는 인터페이스!
  → @FunctionalInterface 어노테이션으로 명시 가능

  ┌────────────────────┬──────────────────────────────────┐
  │ 인터페이스          │ 설명                             │
  ├────────────────────┼──────────────────────────────────┤
  │ Predicate<T>       │ T → boolean (조건 검사)          │
  │ Function<T,R>      │ T → R (변환)                     │
  │ Consumer<T>        │ T → void (소비/출력)             │
  │ Supplier<T>        │ () → T (생성/공급)               │
  │ UnaryOperator<T>   │ T → T (같은 타입 변환)           │
  │ BinaryOperator<T>  │ (T, T) → T (두 값 연산)         │
  │ Comparator<T>      │ (T, T) → int (비교)             │
  └────────────────────┴──────────────────────────────────┘

  ┌──────────────────────────────────────────────────┐
  │  비유: 함수형 인터페이스는 "주문서 양식"          │
  │                                                  │
  │  Predicate: "이것이 맞나요?" 양식 (Yes/No 답변)  │
  │  Function:  "이것을 저것으로 바꿔주세요" 양식    │
  │  Consumer:  "이것을 처리해주세요" 양식            │
  │  Supplier:  "무언가를 만들어주세요" 양식          │
  └──────────────────────────────────────────────────┘
*/

// ─── 직접 만드는 함수형 인터페이스 ──────────────────────
@FunctionalInterface
interface ScoreChecker {
    boolean check(int score);
}


// =====================================================================
// 레슨 3 — Stream API 기초
// =====================================================================
/*
★ Stream = 데이터를 흘려보내며 처리하는 "파이프라인"
  → 컬렉션(List, Set 등)의 데이터를 선언적으로 처리

  ┌──────────────────────────────────────────────────┐
  │  비유: Stream은 "공장 컨베이어 벨트"              │
  │                                                  │
  │  원재료(데이터) → [필터] → [가공] → [포장] → 완성│
  │                                                  │
  │  list.stream()                                   │
  │      .filter(...)    ← 조건에 맞는 것만 통과     │
  │      .map(...)       ← 변환/가공                 │
  │      .collect(...)   ← 결과물 수집               │
  └──────────────────────────────────────────────────┘

★ Stream 연산 종류
  ┌────────────────┬──────────────────────────────────┐
  │ 중간 연산      │ Stream을 반환 (체이닝 가능!)      │
  │ (intermediate) │ filter, map, sorted, distinct,   │
  │                │ limit, skip, flatMap, peek        │
  ├────────────────┼──────────────────────────────────┤
  │ 최종 연산      │ 결과를 반환 (Stream 소비)         │
  │ (terminal)     │ collect, forEach, count, sum,    │
  │                │ min, max, reduce, toArray        │
  └────────────────┴──────────────────────────────────┘

★ 중요: Stream은 1회용! 한번 소비하면 다시 못 씀!
*/


// =====================================================================
// 레슨 4 — map, filter, reduce
// =====================================================================
/*
★ filter: 조건에 맞는 것만 걸러냄
  .filter(x -> x > 0)  ← 양수만 통과

★ map: 각 요소를 변환
  .map(x -> x * 2)  ← 각 요소를 2배로

★ reduce: 모든 요소를 하나로 합침
  .reduce(0, (a, b) -> a + b)  ← 전부 더하기

  ┌──────────────────────────────────────────┐
  │  filter: [1, -2, 3, -4, 5]              │
  │          → [1, 3, 5]  (양수만)          │
  │                                          │
  │  map:    [1, 3, 5]                       │
  │          → [2, 6, 10] (2배)             │
  │                                          │
  │  reduce: [2, 6, 10]                     │
  │          → 18  (전부 합산)              │
  └──────────────────────────────────────────┘
*/


// =====================================================================
// 레슨 5 — Optional
// =====================================================================
/*
★ Optional<T> = "값이 있을 수도 없을 수도 있는 상자"
  → null 대신 사용하여 NullPointerException을 방지!

  ┌──────────────────────────────────────────┐
  │  비유: Optional은 "택배 상자"            │
  │                                          │
  │  상자를 열었을 때:                       │
  │    물건이 있으면 → 사용한다 (isPresent)  │
  │    비어있으면   → 대체품을 쓴다 (orElse)│
  │                                          │
  │  상자를 열지도 않고 바로 쓰면 → 위험!   │
  │  (null에 직접 접근하면 NPE!)             │
  └──────────────────────────────────────────┘

★ Optional 주요 메서드
  ┌──────────────────┬──────────────────────────┐
  │ of(value)        │ null이 아닌 값으로 생성   │
  │ ofNullable(val)  │ null일 수도 있는 값       │
  │ empty()          │ 빈 Optional               │
  │ isPresent()      │ 값이 있으면 true          │
  │ get()            │ 값 꺼내기 (비면 예외!)    │
  │ orElse(기본값)    │ 값이 없으면 기본값        │
  │ orElseThrow()    │ 값이 없으면 예외          │
  │ ifPresent(소비자) │ 값이 있으면 실행          │
  │ map(변환)        │ 값을 변환                 │
  │ filter(조건)     │ 조건에 맞으면 유지        │
  └──────────────────┴──────────────────────────┘
*/


// =====================================================================
// 레슨 6 — 메서드 레퍼런스
// =====================================================================
/*
★ 메서드 레퍼런스 = 이미 있는 메서드를 람다 대신 참조
  → 코드가 더 간결해짐!

  ┌────────────────────────┬──────────────────────┐
  │ 종류                   │ 예시                 │
  ├────────────────────────┼──────────────────────┤
  │ 정적 메서드 참조       │ Integer::parseInt    │
  │ 인스턴스 메서드 참조   │ String::toUpperCase  │
  │ 생성자 참조            │ ArrayList::new       │
  └────────────────────────┴──────────────────────┘

  // 람다
  .map(s -> s.toUpperCase())
  // 메서드 레퍼런스
  .map(String::toUpperCase)
*/


// ─── 학생 레코드 ────────────────────────────────────────
record Student(String name, int score, String club) {}


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {

    public static void main(String[] args) {
        System.out.println("■■■ Java 09단계: 스트림과 람다 ■■■\n");

        // ─── 레슨 1: 람다 기초 ──────────────────────────
        System.out.println("── 레슨 1: 람다식 기초 ──────────────────────────");

        // 전통적인 Comparator (익명 내부 클래스)
        List<String> names = new ArrayList<>(Arrays.asList("Charlie", "Alice", "Bob"));
        System.out.println("  정렬 전: " + names);

        // 람다로 정렬!
        names.sort((a, b) -> a.length() - b.length());
        System.out.println("  길이순 정렬: " + names);

        names.sort((a, b) -> a.compareTo(b));
        System.out.println("  사전순 정렬: " + names);
        System.out.println();

        // ─── 레슨 2: 함수형 인터페이스 ───────────────────
        System.out.println("── 레슨 2: 함수형 인터페이스 ────────────────────");

        // Predicate<T>: T → boolean
        Predicate<Integer> isPositive = n -> n > 0;
        Predicate<Integer> isEven = n -> n % 2 == 0;
        System.out.println("  5는 양수? " + isPositive.test(5));
        System.out.println("  4는 짝수? " + isEven.test(4));
        System.out.println("  5는 양수이면서 짝수? " + isPositive.and(isEven).test(5));

        // Function<T,R>: T → R
        Function<String, Integer> strLen = String::length;
        Function<Integer, String> toGrade = score -> {
            if (score >= 90) return "A";
            if (score >= 80) return "B";
            if (score >= 70) return "C";
            return "F";
        };
        System.out.println("  \"Hello\"의 길이: " + strLen.apply("Hello"));
        System.out.println("  85의 등급: " + toGrade.apply(85));

        // Consumer<T>: T → void
        Consumer<String> shout = s -> System.out.println("  📢 " + s.toUpperCase());
        shout.accept("hello world");

        // Supplier<T>: () → T
        Supplier<Double> randomScore = () -> Math.random() * 100;
        System.out.printf("  랜덤 점수: %.1f%n", randomScore.get());

        // 직접 만든 함수형 인터페이스
        ScoreChecker isPassed = score -> score >= 60;
        System.out.println("  75점 통과? " + isPassed.check(75));
        System.out.println("  55점 통과? " + isPassed.check(55));
        System.out.println();

        // ─── 레슨 3: Stream 기초 ────────────────────────
        System.out.println("── 레슨 3: Stream API 기초 ──────────────────────");

        List<Integer> numbers = Arrays.asList(5, 2, 8, 1, 9, 3, 7, 4, 6);

        // filter: 조건에 맞는 것만
        List<Integer> evens = numbers.stream()
                .filter(n -> n % 2 == 0)
                .collect(Collectors.toList());
        System.out.println("  원본: " + numbers);
        System.out.println("  짝수만: " + evens);

        // map: 변환
        List<Integer> doubled = numbers.stream()
                .map(n -> n * 2)
                .collect(Collectors.toList());
        System.out.println("  2배: " + doubled);

        // sorted: 정렬
        List<Integer> sorted = numbers.stream()
                .sorted()
                .collect(Collectors.toList());
        System.out.println("  오름차순: " + sorted);

        // distinct: 중복 제거
        List<Integer> withDups = Arrays.asList(1, 2, 2, 3, 3, 3, 4);
        List<Integer> unique = withDups.stream()
                .distinct()
                .collect(Collectors.toList());
        System.out.println("  중복 제거: " + withDups + " → " + unique);

        // count, sum, min, max
        long count = numbers.stream().filter(n -> n > 5).count();
        System.out.println("  5보다 큰 수의 개수: " + count);
        System.out.println();

        // ─── 레슨 4: map/filter/reduce ──────────────────
        System.out.println("── 레슨 4: map / filter / reduce ────────────────");

        List<Student> students = Arrays.asList(
            new Student("김철수", 92, "축구부"),
            new Student("이영희", 78, "미술부"),
            new Student("박민수", 55, "축구부"),
            new Student("최지은", 88, "미술부"),
            new Student("정하나", 95, "과학부"),
            new Student("강동원", 62, "축구부")
        );

        // filter + map: 80점 이상 학생의 이름만
        List<String> honorNames = students.stream()
                .filter(s -> s.score() >= 80)
                .map(Student::name)
                .collect(Collectors.toList());
        System.out.println("  80점 이상: " + honorNames);

        // reduce: 점수 합계
        int totalScore = students.stream()
                .map(Student::score)
                .reduce(0, Integer::sum);
        System.out.println("  전체 점수 합계: " + totalScore);
        System.out.printf("  평균 점수: %.1f%n", (double) totalScore / students.size());

        // 최고점, 최저점
        OptionalInt maxScore = students.stream()
                .mapToInt(Student::score)
                .max();
        OptionalInt minScore = students.stream()
                .mapToInt(Student::score)
                .min();
        System.out.println("  최고점: " + maxScore.orElse(0));
        System.out.println("  최저점: " + minScore.orElse(0));

        // groupingBy: 동아리별 그룹
        Map<String, List<Student>> byClub = students.stream()
                .collect(Collectors.groupingBy(Student::club));
        System.out.println("  동아리별 학생:");
        byClub.forEach((club, members) -> {
            System.out.print("    " + club + ": ");
            members.forEach(s -> System.out.print(s.name() + "(" + s.score() + ") "));
            System.out.println();
        });

        // 동아리별 평균 점수
        Map<String, Double> avgByClub = students.stream()
                .collect(Collectors.groupingBy(
                        Student::club,
                        Collectors.averagingInt(Student::score)
                ));
        System.out.println("  동아리별 평균:");
        avgByClub.forEach((club, avg) ->
                System.out.printf("    %s: %.1f점%n", club, avg));
        System.out.println();

        // ─── 레슨 5: Optional ───────────────────────────
        System.out.println("── 레슨 5: Optional ─────────────────────────────");

        // Optional 기본 사용
        Optional<String> present = Optional.of("Hello");
        Optional<String> empty = Optional.empty();
        Optional<String> nullable = Optional.ofNullable(null);

        System.out.println("  present 값: " + present.orElse("없음"));
        System.out.println("  empty 값: " + empty.orElse("없음"));
        System.out.println("  nullable 값: " + nullable.orElse("없음"));

        // Optional과 Stream 조합
        Optional<Student> topStudent = students.stream()
                .max(Comparator.comparingInt(Student::score));

        topStudent.ifPresent(s ->
                System.out.println("  1등: " + s.name() + " (" + s.score() + "점)"));

        // find + Optional
        Optional<Student> found = students.stream()
                .filter(s -> s.name().equals("이영희"))
                .findFirst();
        String foundName = found.map(Student::name).orElse("못 찾음");
        System.out.println("  검색 결과: " + foundName);

        Optional<Student> notFound = students.stream()
                .filter(s -> s.name().equals("없는사람"))
                .findFirst();
        System.out.println("  못 찾은 결과: " + notFound.map(Student::name).orElse("없음"));
        System.out.println();

        // ─── 레슨 6: 메서드 레퍼런스 ────────────────────
        System.out.println("── 레슨 6: 메서드 레퍼런스 ──────────────────────");

        List<String> words = Arrays.asList("hello", "world", "java", "stream");

        // 람다 vs 메서드 레퍼런스
        List<String> upper1 = words.stream()
                .map(s -> s.toUpperCase())     // 람다
                .collect(Collectors.toList());
        List<String> upper2 = words.stream()
                .map(String::toUpperCase)       // 메서드 레퍼런스 (더 간결!)
                .collect(Collectors.toList());

        System.out.println("  람다:          " + upper1);
        System.out.println("  메서드 레퍼런스: " + upper2);

        // 정적 메서드 참조
        List<String> numStrings = Arrays.asList("1", "2", "3", "4", "5");
        List<Integer> parsed = numStrings.stream()
                .map(Integer::parseInt)  // 정적 메서드 참조
                .collect(Collectors.toList());
        System.out.println("  파싱 결과: " + parsed);

        // forEach + 메서드 레퍼런스
        System.out.print("  출력: ");
        parsed.forEach(n -> System.out.print(n + " "));
        System.out.println();
        System.out.println();

        // ─── 종합 예제: 성적 분석 시스템 ─────────────────
        System.out.println("── 종합 예제: 성적 분석 시스템 ──────────────────");

        // 통과/미통과 분류
        Map<Boolean, List<Student>> passPartition = students.stream()
                .collect(Collectors.partitioningBy(s -> s.score() >= 60));

        System.out.println("  통과자:");
        passPartition.get(true).forEach(s ->
                System.out.println("    ✓ " + s.name() + " (" + s.score() + "점)"));
        System.out.println("  미통과자:");
        passPartition.get(false).forEach(s ->
                System.out.println("    ✗ " + s.name() + " (" + s.score() + "점)"));

        // 점수대별 분류 (10점 단위)
        Map<Integer, Long> scoreDistribution = students.stream()
                .collect(Collectors.groupingBy(
                        s -> (s.score() / 10) * 10,
                        Collectors.counting()
                ));
        System.out.println("  점수 분포:");
        new TreeMap<>(scoreDistribution).forEach((range, cnt) ->
                System.out.println("    " + range + "~" + (range + 9) + "점: " + cnt + "명"));

        // 이름 목록을 문자열로 합치기
        String allNames = students.stream()
                .map(Student::name)
                .collect(Collectors.joining(", "));
        System.out.println("  전체 학생: " + allNames);
        System.out.println();

        System.out.println("■■■ 09단계 학습 완료! ■■■");
    }
}
