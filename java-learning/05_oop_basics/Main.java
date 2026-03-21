/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 05단계: 객체지향 프로그래밍 기초 (OOP Basics)
  ─ 클래스, 생성자, this, 캡슐화, static, toString, equals ─

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  객체지향 프로그래밍(OOP)이란?
  현실 세계의 것들을 프로그램으로 표현하는 방법이에요!
  강아지, 자동차, 학생... 모든 것을 "객체"로 만들 수 있어요!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

/*
┌─────────────────────────────────────────────────────────────┐
│  Student 클래스 - 학생을 표현하는 설계도                      │
│                                                             │
│  클래스는 "설계도"예요.                                       │
│  강아지 설계도를 만들면 → 여러 마리의 강아지를 만들 수 있듯이 │
│  Student 설계도로 → 여러 명의 학생 객체를 만들 수 있어요!     │
└─────────────────────────────────────────────────────────────┘
*/
class Student {

    /*
     * 필드(Field) = 객체의 데이터를 저장하는 변수
     *
     * 접근 제어자:
     * private  = 이 클래스 안에서만 접근 가능 (가장 제한적)
     * protected = 같은 패키지 + 자식 클래스 접근 가능
     * (없음)   = 같은 패키지에서만 접근 가능
     * public   = 어디서든 접근 가능 (가장 개방적)
     *
     * 캡슐화: 데이터(필드)를 private으로 숨기고,
     * getter/setter를 통해서만 접근하게 해요!
     * 마치 은행 금고처럼 아무나 돈을 꺼낼 수 없고
     * 직원(getter/setter)을 통해야 하는 것처럼요.
     */
    private String name;      // 이름
    private int age;          // 나이
    private double grade;     // 성적 (0.0 ~ 100.0)
    private String school;    // 학교

    // static 필드 = 모든 객체가 공유하는 변수
    // 학생 수를 세는 카운터 - 모든 Student 객체가 공유해요!
    // 마치 학교 게시판처럼 모든 학생이 같은 게시판을 봐요.
    private static int totalCount = 0;

    /*
     * 생성자(Constructor)
     *
     * 객체를 만들 때 자동으로 실행되는 특별한 메서드예요!
     * 마치 태어날 때 이름을 붙여주는 것처럼요.
     *
     * 특징:
     * - 클래스 이름과 똑같아요
     * - 반환 타입이 없어요 (void도 아님!)
     * - new 키워드로 객체를 만들 때 자동 호출돼요
     */

    // 기본 생성자 (Default Constructor)
    // 매개변수 없는 생성자 - 아무 정보 없이 학생을 만들어요
    public Student() {
        this.name = "이름없음";
        this.age = 0;
        this.grade = 0.0;
        this.school = "미정";
        totalCount++;  // 학생이 만들어질 때마다 카운트 증가
        System.out.println("기본 생성자로 학생 생성됨");
    }

    // 매개변수 있는 생성자 (Parameterized Constructor)
    // 이름, 나이, 성적, 학교를 받아서 학생을 만들어요
    public Student(String name, int age, double grade, String school) {
        /*
         * this 키워드란?
         *
         * "나 자신(현재 객체)"을 가리켜요.
         * 여기서 this.name은 "이 객체의 name 필드"를 말해요.
         * 매개변수 name과 필드 name을 구별할 때 써요!
         *
         * 마치 자기소개할 때 "제 이름은 김철수예요"에서
         * "제"가 this와 같아요!
         */
        this.name = name;      // 매개변수 name → 필드 name에 저장
        this.age = age;
        this.grade = grade;
        this.school = school;
        totalCount++;
    }

    // this() 생성자 호출 - 다른 생성자를 재사용
    public Student(String name, int age) {
        // 이미 만들어진 생성자를 재사용해요!
        // 반드시 첫 줄에 있어야 해요.
        this(name, age, 0.0, "미정");
    }

    // ─── Getter 메서드 ────────────────────────────────────
    // private 필드를 외부에서 읽을 수 있도록 해주는 메서드
    // "get" + 필드이름 형식으로 짓는 것이 관례예요

    public String getName() { return name; }
    public int getAge() { return age; }
    public double getGrade() { return grade; }
    public String getSchool() { return school; }

    // static 필드는 static 메서드로!
    public static int getTotalCount() { return totalCount; }

    // ─── Setter 메서드 ────────────────────────────────────
    // private 필드를 외부에서 수정할 수 있도록 해주는 메서드
    // "set" + 필드이름 형식으로 짓는 것이 관례예요
    // 유효성 검사를 할 수 있어요! (나쁜 값 막기)

    public void setName(String name) {
        if (name == null || name.isBlank()) {
            System.out.println("이름은 빈값일 수 없어요!");
            return;
        }
        this.name = name;
    }

    public void setAge(int age) {
        if (age < 0 || age > 150) {
            System.out.println("나이가 이상해요: " + age);
            return;
        }
        this.age = age;
    }

    public void setGrade(double grade) {
        if (grade < 0.0 || grade > 100.0) {
            System.out.println("성적은 0~100 사이여야 해요!");
            return;
        }
        this.grade = grade;
    }

    public void setSchool(String school) {
        this.school = school;
    }

    // ─── 일반 메서드 ──────────────────────────────────────

    // 학생 정보 출력
    public void introduce() {
        System.out.println("안녕하세요! 저는 " + school + "에 다니는 " +
                            age + "살 " + name + "입니다. 성적: " + grade + "점");
    }

    // 학점 계산
    public String getLetterGrade() {
        if (grade >= 90) return "A";
        else if (grade >= 80) return "B";
        else if (grade >= 70) return "C";
        else if (grade >= 60) return "D";
        else return "F";
    }

    /*
     * toString() 메서드 오버라이드
     *
     * System.out.println(객체)를 하면 자동으로 호출되는 메서드예요!
     * 기본값은 "클래스이름@해시코드"인데 알아보기 어려워요.
     * 우리가 원하는 형태로 바꿔서 출력할 수 있어요!
     */
    @Override
    public String toString() {
        return String.format("Student{이름='%s', 나이=%d, 성적=%.1f, 학교='%s'}",
                              name, age, grade, school);
    }

    /*
     * equals() 메서드 오버라이드
     *
     * 두 객체가 "같은지" 비교해요.
     * 기본 equals()는 주소(참조)를 비교해요.
     * 우리는 이름과 학교가 같으면 같은 학생으로 보고 싶어요!
     */
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;   // 같은 객체면 true
        if (!(obj instanceof Student)) return false;  // Student가 아니면 false
        Student other = (Student) obj;  // Student로 형변환
        return this.name.equals(other.name) && this.school.equals(other.school);
    }

    /*
     * hashCode() 메서드
     *
     * equals()를 오버라이드하면 hashCode()도 같이 오버라이드해야 해요!
     * HashMap, HashSet에서 객체를 구별할 때 사용해요.
     */
    @Override
    public int hashCode() {
        return (name + school).hashCode();
    }
}

/*
┌─────────────────────────────────────────────────────────────┐
│  BankAccount 클래스 - 캡슐화의 좋은 예제                      │
│                                                             │
│  잔액(balance)을 private으로 보호해요.                       │
│  마음대로 잔액을 바꿀 수 없고, 입금/출금 메서드만 사용 가능!   │
└─────────────────────────────────────────────────────────────┘
*/
class BankAccount {
    private String owner;      // 계좌 주인
    private double balance;    // 잔액 (외부에서 직접 변경 불가!)
    private static double interestRate = 0.02;  // 이자율 (모든 계좌 공통)

    public BankAccount(String owner, double initialBalance) {
        this.owner = owner;
        this.balance = (initialBalance >= 0) ? initialBalance : 0;
    }

    // 입금 메서드
    public void deposit(double amount) {
        if (amount <= 0) {
            System.out.println("입금액은 0보다 커야 해요!");
            return;
        }
        balance += amount;
        System.out.printf("%s님 %,.0f원 입금 → 잔액: %,.0f원%n", owner, amount, balance);
    }

    // 출금 메서드
    public boolean withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("출금액은 0보다 커야 해요!");
            return false;
        }
        if (amount > balance) {
            System.out.println("잔액이 부족해요! 잔액: " + balance + "원");
            return false;
        }
        balance -= amount;
        System.out.printf("%s님 %,.0f원 출금 → 잔액: %,.0f원%n", owner, amount, balance);
        return true;
    }

    // 이자 추가
    public void addInterest() {
        double interest = balance * interestRate;
        balance += interest;
        System.out.printf("이자 %,.0f원 추가 → 잔액: %,.0f원%n", interest, balance);
    }

    public double getBalance() { return balance; }
    public String getOwner() { return owner; }
    public static double getInterestRate() { return interestRate; }

    @Override
    public String toString() {
        return String.format("BankAccount{주인='%s', 잔액=%,.0f원}", owner, balance);
    }
}

/*
┌─────────────────────────────────────────────────────────────┐
│  Counter 클래스 - static 멤버 이해하기                        │
│                                                             │
│  static = 클래스 자체에 속하는 것 (객체마다 각자 없고 공유!)  │
└─────────────────────────────────────────────────────────────┘
*/
class Counter {
    private int count;           // 인스턴스 변수 (각 객체마다 따로 있어요)
    private static int total = 0; // static 변수 (모든 객체가 공유해요!)

    public Counter() {
        this.count = 0;
    }

    public void increment() {
        count++;   // 이 객체의 count만 증가
        total++;   // 모든 객체의 공유 total도 증가
    }

    public int getCount() { return count; }
    public static int getTotal() { return total; }  // static 메서드
}

// ─── Main 클래스 ──────────────────────────────────────────────
public class Main {

    public static void main(String[] args) {

        System.out.println("=== 05단계: 객체지향 프로그래밍 기초 ===");
        System.out.println();

        // ── Student 객체 만들기 ───────────────────────────
        System.out.println("[ 학생 객체 만들기 ]");

        // new 키워드로 객체 생성 → 생성자 자동 호출!
        Student s1 = new Student("김철수", 12, 95.5, "행복초등학교");
        Student s2 = new Student("이영희", 11, 88.0, "행복초등학교");
        Student s3 = new Student("박민준", 13);  // 두 매개변수 생성자
        Student s4 = new Student();              // 기본 생성자

        System.out.println("\n학생 정보:");
        System.out.println(s1);  // toString() 자동 호출
        System.out.println(s2);
        System.out.println(s3);
        System.out.println(s4);

        System.out.println("\n총 학생 수: " + Student.getTotalCount() + "명");

        // ── 메서드 호출 ───────────────────────────────────
        System.out.println("\n[ 메서드 호출 ]");
        s1.introduce();
        System.out.println(s1.getName() + "의 학점: " + s1.getLetterGrade());

        // ── setter로 값 변경 ──────────────────────────────
        System.out.println("\n[ Setter로 값 변경 ]");
        s3.setName("박민준");
        s3.setAge(13);
        s3.setGrade(82.5);
        s3.setSchool("미래초등학교");
        System.out.println("변경 후: " + s3);

        // 잘못된 값 설정 시도
        System.out.println("\n잘못된 값 설정 시도:");
        s1.setAge(-5);       // 나이 -5? 불가!
        s1.setGrade(150.0);  // 성적 150? 불가!

        // ── equals() 테스트 ───────────────────────────────
        System.out.println("\n[ equals() 비교 ]");
        Student copy = new Student("김철수", 12, 95.5, "행복초등학교");
        System.out.println("s1 == copy: " + (s1 == copy));           // false (다른 객체)
        System.out.println("s1.equals(copy): " + s1.equals(copy));   // true (이름+학교 같음)
        System.out.println("s1.equals(s2): " + s1.equals(s2));       // false (이름 다름)

        System.out.println();

        // ── BankAccount 테스트 ────────────────────────────
        System.out.println("[ 은행 계좌 (캡슐화 예제) ]");

        BankAccount account1 = new BankAccount("김철수", 100000);
        BankAccount account2 = new BankAccount("이영희", 50000);

        System.out.println(account1);
        System.out.println(account2);

        System.out.println("\n거래 내역:");
        account1.deposit(50000);     // 5만원 입금
        account1.withdraw(30000);    // 3만원 출금
        account1.withdraw(200000);   // 20만원 출금 (잔액 부족!)
        account1.addInterest();      // 이자 추가

        System.out.println("\n이자율: " + (BankAccount.getInterestRate() * 100) + "%");
        System.out.println("최종 잔액: " + account1);

        System.out.println();

        // ── static 멤버 테스트 ────────────────────────────
        System.out.println("[ static 멤버 테스트 ]");
        Counter c1 = new Counter();
        Counter c2 = new Counter();
        Counter c3 = new Counter();

        c1.increment(); c1.increment(); c1.increment();  // c1: 3번
        c2.increment(); c2.increment();                  // c2: 2번
        c3.increment();                                  // c3: 1번

        System.out.println("c1 개수: " + c1.getCount());  // 3 (c1만의 카운트)
        System.out.println("c2 개수: " + c2.getCount());  // 2 (c2만의 카운트)
        System.out.println("c3 개수: " + c3.getCount());  // 1 (c3만의 카운트)
        System.out.println("전체 합: " + Counter.getTotal()); // 6 (모든 객체 공유!)

        System.out.println();
        System.out.println("╔════════════════════════════════════════════╗");
        System.out.println("║  05단계 OOP 기초 학습 완료! 이제 진짜 시작! ║");
        System.out.println("╚════════════════════════════════════════════╝");
    }
}
