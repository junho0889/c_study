/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 07단계: 인터페이스와 제네릭
  ─ interface, default, generic, 와일드카드, 타입 바운드 ─

  [학습 목표]
  1. 인터페이스의 다양한 활용법을 안다
  2. default/static 메서드를 이해한다
  3. 제네릭(Generic)의 개념과 문법을 안다
  4. 와일드카드(?)와 바운드(<T extends ...>)를 이해한다
  5. 제네릭 클래스/메서드를 직접 만들 수 있다

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


// =====================================================================
// 레슨 1 — 인터페이스 심화
// =====================================================================
/*
★ 인터페이스 = "이런 능력이 있습니다"라는 약속

  ┌──────────────────────────────────────────┐
  │  비유: 인터페이스는 "자격증"              │
  │                                          │
  │  수영 자격증(Swimmable):                 │
  │    → swim() 할 수 있다!                  │
  │                                          │
  │  운전 자격증(Drivable):                  │
  │    → drive() 할 수 있다!                 │
  │                                          │
  │  한 사람이 자격증 여러 개 = 다중 구현!    │
  └──────────────────────────────────────────┘

★ Java 8 이후 인터페이스 진화
  ┌────────────────┬───────────────────────────┐
  │ 메서드 종류    │ 설명                       │
  ├────────────────┼───────────────────────────┤
  │ 추상 메서드    │ 구현 없음 (반드시 오버라이딩)│
  │ default 메서드 │ 구현 있음 (선택적 오버라이딩)│
  │ static 메서드  │ 인터페이스 이름으로 호출   │
  │ private 메서드 │ 인터페이스 내부에서만 사용  │
  └────────────────┴───────────────────────────┘
*/

// ─── 인터페이스 정의 ────────────────────────────────────
interface Printable {
    String toPrintString();  // 추상 메서드

    // ★ default 메서드: 기본 구현 제공
    default void print() {
        System.out.println("  [출력] " + toPrintString());
    }

    // ★ static 메서드: 유틸리티 기능
    static void printSeparator() {
        System.out.println("  ──────────────────────────");
    }
}

interface Scorable {
    int getScore();
    String getGrade();

    // default 메서드: 통과 여부
    default boolean isPassed() {
        return getScore() >= 60;
    }
}

// ─── 여러 인터페이스 동시 구현 ──────────────────────────
class StudentReport implements Printable, Scorable {
    private final String name;
    private final int score;

    StudentReport(String name, int score) {
        this.name = name;
        this.score = score;
    }

    @Override
    public String toPrintString() {
        return name + " 학생: " + score + "점 [" + getGrade() + "]";
    }

    @Override
    public int getScore() {
        return score;
    }

    @Override
    public String getGrade() {
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 70) return "C";
        if (score >= 60) return "D";
        return "F";
    }

    String getName() {
        return name;
    }
}


// =====================================================================
// 레슨 2 — 인터페이스를 타입으로 사용
// =====================================================================
/*
★ 인터페이스도 변수의 타입으로 사용 가능!
  → Printable p = new StudentReport(...)
  → p.print();  ← Printable의 메서드만 호출 가능

  이것이 바로 "다형성"!
  → 구체적인 클래스를 몰라도 인터페이스만 알면 사용 가능
*/

class TeacherReport implements Printable {
    private final String name;
    private final String subject;

    TeacherReport(String name, String subject) {
        this.name = name;
        this.subject = subject;
    }

    @Override
    public String toPrintString() {
        return name + " 선생님 - 담당: " + subject;
    }
}


// =====================================================================
// 레슨 3 — Comparable 인터페이스 (정렬)
// =====================================================================
/*
★ Comparable<T> = "비교 가능한 객체"라는 약속
  → compareTo() 메서드를 구현하면 자동으로 정렬 가능!

  ┌─────────────────────────────────────────┐
  │  compareTo() 반환값 규칙:               │
  │                                         │
  │  음수(-) → this가 더 앞(작음)           │
  │  0       → 같음                         │
  │  양수(+) → this가 더 뒤(큼)             │
  └─────────────────────────────────────────┘
*/

class SortableStudent implements Comparable<SortableStudent> {
    final String name;
    final int score;

    SortableStudent(String name, int score) {
        this.name = name;
        this.score = score;
    }

    @Override
    public int compareTo(SortableStudent other) {
        // 점수 내림차순 (높은 점수가 먼저)
        return Integer.compare(other.score, this.score);
    }

    @Override
    public String toString() {
        return name + "(" + score + "점)";
    }
}


// =====================================================================
// 레슨 4 — 제네릭 기초
// =====================================================================
/*
★ 제네릭 = "타입을 나중에 결정한다"
  → 코드를 쓸 때는 <T>라고 비워두고, 사용할 때 <String>, <Integer> 등으로 채움

  ┌──────────────────────────────────────────┐
  │  비유: 제네릭은 "빈칸 채우기"             │
  │                                          │
  │  상자<   > ← 어떤 물건이든 넣을 수 있음  │
  │  상자<과일> ← 과일만 넣겠다!             │
  │  상자<책>   ← 책만 넣겠다!               │
  │                                          │
  │  상자의 구조는 같지만 내용물이 다름!      │
  └──────────────────────────────────────────┘

★ 제네릭을 쓰는 이유
  1. 타입 안전성: 잘못된 타입을 넣으면 컴파일 에러
  2. 코드 재사용: 하나의 클래스로 여러 타입 처리
  3. 캐스팅 불필요: 꺼낼 때 (String) 같은 형변환 안 해도 됨

★ 제네릭이 없던 시절 (Java 5 이전)
  List list = new ArrayList();
  list.add("hello");
  list.add(123);        // ← 아무거나 다 들어감! 위험!
  String s = (String) list.get(1);  // ← 런타임 에러! ClassCastException

★ 제네릭 도입 후
  List<String> list = new ArrayList<>();
  list.add("hello");
  list.add(123);        // ← 컴파일 에러! 안전!
  String s = list.get(0);  // ← 캐스팅 불필요!
*/

// ─── 제네릭 클래스 만들기 ───────────────────────────────
// T = Type Parameter (타입 매개변수)
class Box<T> {
    private T item;

    Box(T item) {
        this.item = item;
    }

    T getItem() {
        return item;
    }

    void setItem(T item) {
        this.item = item;
    }

    @Override
    public String toString() {
        return "Box[" + item + "]";
    }
}

// ─── 제네릭 타입 매개변수 여러 개 ────────────────────────
/*
★ 관례적 타입 매개변수 이름
  ┌────┬──────────────┐
  │ T  │ Type         │
  │ E  │ Element      │
  │ K  │ Key          │
  │ V  │ Value        │
  │ N  │ Number       │
  │ R  │ Return type  │
  └────┴──────────────┘
*/

class Pair<K, V> {
    private final K key;
    private final V value;

    Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    K getKey() { return key; }
    V getValue() { return value; }

    @Override
    public String toString() {
        return key + " → " + value;
    }
}


// =====================================================================
// 레슨 5 — 제네릭 메서드
// =====================================================================
/*
★ 클래스 전체가 아니라 메서드 하나만 제네릭으로 만들 수도 있음!
  → <T>를 반환 타입 앞에 선언

  static <T> T firstItem(List<T> list) {
      return list.get(0);
  }
*/


// =====================================================================
// 레슨 6 — 타입 바운드 (extends)
// =====================================================================
/*
★ <T extends Number> = "T는 Number의 자식이어야 한다"
  → T에 아무 타입이나 들어오는 게 아니라 범위를 제한!

  ┌──────────────────────────────────────────┐
  │  비유: "VIP 전용 라운지"                  │
  │                                          │
  │  <T>                → 아무나 입장 가능    │
  │  <T extends Number> → 숫자만 입장 가능    │
  │  <T extends Comparable<T>>               │
  │                     → 비교 가능한 것만!   │
  └──────────────────────────────────────────┘

★ extends vs super (바운드)
  ┌────────────────────┬─────────────────────────┐
  │ <T extends 상한>   │ T는 상한의 하위 타입    │
  │ <? super 하한>     │ ?는 하한의 상위 타입    │
  ├────────────────────┼─────────────────────────┤
  │ 읽기에 적합        │ 쓰기에 적합             │
  │ (Producer Extends) │ (Consumer Super)        │
  └────────────────────┴─────────────────────────┘
  → 이것을 PECS 원칙이라 부름!
*/

class MathBox<T extends Number> {
    private final T value;

    MathBox(T value) {
        this.value = value;
    }

    double doubleValue() {
        return value.doubleValue();  // Number의 메서드 사용 가능!
    }

    boolean isPositive() {
        return value.doubleValue() > 0;
    }
}


// =====================================================================
// 레슨 7 — 와일드카드 (?)
// =====================================================================
/*
★ 와일드카드 ? = "무엇이든" (unknown type)

  ┌──────────────────────────────────────────────────────┐
  │  List<?>              → 아무 타입의 리스트           │
  │  List<? extends Number> → Number 이하 타입의 리스트  │
  │  List<? super Integer>  → Integer 이상 타입의 리스트 │
  └──────────────────────────────────────────────────────┘

★ 왜 List<Object>가 아니라 List<?>를 쓸까?
  → List<String>은 List<Object>의 하위 타입이 아님! (제네릭은 불변)
  → List<?>는 모든 List<T>를 받을 수 있음!
*/


// =====================================================================
//  메인 실행
// =====================================================================
public class Main {

    // ─── 제네릭 메서드 ──────────────────────────────────
    static <T> T firstItem(List<T> list) {
        if (list.isEmpty()) return null;
        return list.get(0);
    }

    static <T extends Comparable<T>> T findMax(List<T> list) {
        T max = list.get(0);
        for (T item : list) {
            if (item.compareTo(max) > 0) {
                max = item;
            }
        }
        return max;
    }

    // ─── 와일드카드 메서드 ──────────────────────────────
    // ? extends Number → Number의 하위 타입만 받음 (읽기 전용)
    static double sumOfList(List<? extends Number> list) {
        double sum = 0;
        for (Number n : list) {
            sum += n.doubleValue();
        }
        return sum;
    }

    // ?  → 아무 타입이나 받음
    static void printList(List<?> list) {
        for (Object item : list) {
            System.out.print("  " + item);
        }
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("■■■ Java 07단계: 인터페이스와 제네릭 ■■■\n");

        // ─── 레슨 1: 인터페이스 심화 ─────────────────────
        System.out.println("── 레슨 1: 인터페이스 심화 ──────────────────────");
        StudentReport sr1 = new StudentReport("김철수", 92);
        StudentReport sr2 = new StudentReport("이영희", 78);
        StudentReport sr3 = new StudentReport("박민수", 55);

        sr1.print();  // Printable의 default 메서드
        sr2.print();
        sr3.print();

        Printable.printSeparator();  // static 메서드
        System.out.println("  " + sr1.getName() + " 통과 여부: " + sr1.isPassed());
        System.out.println("  " + sr3.getName() + " 통과 여부: " + sr3.isPassed());
        System.out.println();

        // ─── 레슨 2: 인터페이스 타입으로 사용 ────────────
        System.out.println("── 레슨 2: 인터페이스를 타입으로 사용 ───────────");
        Printable[] printables = {
            new StudentReport("홍길동", 88),
            new TeacherReport("김선생", "수학"),
            new StudentReport("성춘향", 95),
            new TeacherReport("이선생", "국어")
        };

        for (Printable p : printables) {
            p.print();  // 어떤 클래스인지 몰라도 OK! 다형성!
        }
        System.out.println();

        // ─── 레슨 3: Comparable 정렬 ─────────────────────
        System.out.println("── 레슨 3: Comparable로 정렬 ────────────────────");
        List<SortableStudent> students = new ArrayList<>(Arrays.asList(
            new SortableStudent("김", 72),
            new SortableStudent("이", 95),
            new SortableStudent("박", 88),
            new SortableStudent("최", 64)
        ));

        System.out.println("  정렬 전: " + students);
        students.sort(null);  // Comparable의 compareTo() 사용
        System.out.println("  정렬 후: " + students);
        System.out.println();

        // ─── 레슨 4: 제네릭 기초 ─────────────────────────
        System.out.println("── 레슨 4: 제네릭 기초 ──────────────────────────");
        Box<String> stringBox = new Box<>("안녕하세요");
        Box<Integer> intBox = new Box<>(42);
        Box<Double> doubleBox = new Box<>(3.14);

        System.out.println("  " + stringBox);
        System.out.println("  " + intBox);
        System.out.println("  " + doubleBox);

        // stringBox.setItem(123);  // ★ 컴파일 에러! 타입 안전성!

        Pair<String, Integer> grade = new Pair<>("김철수", 92);
        Pair<Integer, String> idName = new Pair<>(1, "이영희");
        System.out.println("  " + grade);
        System.out.println("  " + idName);
        System.out.println();

        // ─── 레슨 5: 제네릭 메서드 ──────────────────────
        System.out.println("── 레슨 5: 제네릭 메서드 ────────────────────────");
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
        List<Integer> numbers = Arrays.asList(10, 20, 30);

        System.out.println("  첫 번째 이름: " + firstItem(names));
        System.out.println("  첫 번째 숫자: " + firstItem(numbers));

        System.out.println("  최대 숫자: " + findMax(numbers));
        System.out.println("  최대 이름(사전순): " + findMax(names));
        System.out.println();

        // ─── 레슨 6: 타입 바운드 ─────────────────────────
        System.out.println("── 레슨 6: 타입 바운드 (<T extends ...>) ────────");
        MathBox<Integer> mbi = new MathBox<>(42);
        MathBox<Double> mbd = new MathBox<>(-3.14);

        System.out.println("  Integer MathBox: " + mbi.doubleValue()
                + ", 양수? " + mbi.isPositive());
        System.out.println("  Double MathBox: " + mbd.doubleValue()
                + ", 양수? " + mbd.isPositive());

        // MathBox<String> mbs = new MathBox<>("text");
        // ★ 컴파일 에러! String은 Number를 상속하지 않음!
        System.out.println();

        // ─── 레슨 7: 와일드카드 ─────────────────────────
        System.out.println("── 레슨 7: 와일드카드 (?) ───────────────────────");
        List<Integer> intList = Arrays.asList(1, 2, 3, 4, 5);
        List<Double> doubleList = Arrays.asList(1.5, 2.5, 3.5);

        // ★ ? extends Number → Integer, Double 모두 받음!
        System.out.println("  Integer 합계: " + sumOfList(intList));
        System.out.println("  Double 합계: " + sumOfList(doubleList));

        // ★ ? → 아무 타입이나 출력!
        System.out.print("  정수 리스트:");
        printList(intList);
        System.out.print("  실수 리스트:");
        printList(doubleList);
        System.out.print("  문자열 리스트:");
        printList(names);
        System.out.println();

        // ─── 종합 예제: 제네릭 스택 ─────────────────────
        System.out.println("── 종합 예제: 제네릭 스택 ───────────────────────");
        SimpleStack<String> stack = new SimpleStack<>(5);
        stack.push("첫번째");
        stack.push("두번째");
        stack.push("세번째");

        System.out.println("  peek: " + stack.peek());
        System.out.println("  pop:  " + stack.pop());
        System.out.println("  pop:  " + stack.pop());
        System.out.println("  size: " + stack.size());
        System.out.println();

        System.out.println("■■■ 07단계 학습 완료! ■■■");
    }
}


// =====================================================================
// 종합 예제 — 제네릭 스택 구현
// =====================================================================
/*
★ 제네릭으로 만든 스택(Stack)
  → 어떤 타입이든 저장할 수 있는 "접시 쌓기" 자료구조!

  ┌──────────────────┐
  │  push("세번째")  │ ← 맨 위에 추가
  │  push("두번째")  │
  │  push("첫번째")  │ ← 맨 아래
  └──────────────────┘
  pop() → "세번째" (맨 위부터 꺼냄 = LIFO)
*/
class SimpleStack<T> {
    private final Object[] data;  // ★ 제네릭 배열은 직접 못 만듦 → Object[] 사용
    private int top;

    SimpleStack(int capacity) {
        data = new Object[capacity];
        top = -1;
    }

    void push(T item) {
        if (top >= data.length - 1) {
            System.out.println("  ★ 스택이 가득 찼습니다!");
            return;
        }
        data[++top] = item;
    }

    @SuppressWarnings("unchecked")
    T pop() {
        if (top < 0) {
            System.out.println("  ★ 스택이 비어있습니다!");
            return null;
        }
        return (T) data[top--];
    }

    @SuppressWarnings("unchecked")
    T peek() {
        if (top < 0) return null;
        return (T) data[top];
    }

    int size() {
        return top + 1;
    }

    boolean isEmpty() {
        return top < 0;
    }
}
