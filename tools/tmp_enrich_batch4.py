# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(path: str, content: str) -> None:
    file_path = ROOT / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content.strip() + "\n", encoding="utf-8")


def main() -> None:
    write(
        "java-learning/06_inheritance_polymorphism/Main.java",
        r'''
/*
===============================================================================
  Java 학습 06단계: 상속과 다형성

  목표:
  1. 상속이 왜 필요한지 이해합니다.
  2. 부모 타입으로 자식 객체를 다루는 이유를 배웁니다.
  3. 오버라이딩이 "같은 버튼, 다른 동작"이라는 점을 익힙니다.
===============================================================================
*/

abstract class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    void introduce() {
        System.out.println("  저는 " + name + " 입니다.");
    }

    abstract void speak();
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }

    @Override
    void speak() {
        System.out.println("  멍멍! 강아지는 짖는 방식으로 자기 생각을 표현합니다.");
    }
}

class Cat extends Animal {
    Cat(String name) {
        super(name);
    }

    @Override
    void speak() {
        System.out.println("  야옹! 고양이는 다른 소리로 같은 역할을 합니다.");
    }
}

public class Main {
    static void lesson1WhyInheritance() {
        /*
         * 상속은 "겹치는 설명을 부모에게 모으는 기술"입니다.
         * 형제자매가 같은 성씨를 공유하는 것처럼,
         * 동물들이 공통으로 가지는 이름, 소개 기능을 부모 클래스에 모아 둡니다.
         */
        System.out.println("[레슨 1] 상속이 왜 필요할까?");
        System.out.println("  공통 코드를 한 곳에 모으면 수정할 때 덜 힘듭니다.");
        System.out.println("  Dog 와 Cat 이 둘 다 name 필드를 따로 만들 필요가 없습니다.");
        System.out.println();
    }

    static void lesson2Polymorphism() {
        /*
         * 다형성은 "겉모습은 하나, 실제 동작은 여러 개"라고 생각하면 쉽습니다.
         * 리모컨의 전원 버튼은 하나지만, TV 마다 실제 반응은 다를 수 있습니다.
         */
        Animal[] animals = {
            new Dog("초코"),
            new Cat("나비")
        };

        System.out.println("[레슨 2] 다형성 예제");
        for (Animal animal : animals) {
            animal.introduce();
            animal.speak();
        }
        System.out.println();
    }

    static void lesson3WhyOverrideWorks() {
        System.out.println("[레슨 3] 왜 오버라이딩이 중요할까?");
        System.out.println("  부모 타입 Animal 로 묶어서 다뤄도");
        System.out.println("  실제 객체가 Dog 인지 Cat 인지에 따라 speak() 결과가 달라집니다.");
        System.out.println("  이것이 다형성의 핵심입니다.");
        System.out.println();
    }

    static void lesson4CommonMistakes() {
        System.out.println("[레슨 4] 자주 하는 실수");
        System.out.println("  1. 상속을 '코드 재사용 기계'처럼만 생각하고 관계를 무시합니다.");
        System.out.println("  2. 부모-자식이 아닌데도 억지로 상속으로 묶습니다.");
        System.out.println("  3. 오버라이딩 없이 부모 메서드만 쓰면서 다형성이 없다고 착각합니다.");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 06단계 : 상속과 다형성");
        System.out.println("============================================================");
        System.out.println();

        lesson1WhyInheritance();
        lesson2Polymorphism();
        lesson3WhyOverrideWorks();
        lesson4CommonMistakes();
    }
}
''',
    )

    write(
        "java-learning/07_interfaces_generics/Main.java",
        r'''
/*
===============================================================================
  Java 학습 07단계: 인터페이스와 제네릭
===============================================================================
*/

interface Payable {
    void pay(int amount);
}

class CardPayment implements Payable {
    @Override
    public void pay(int amount) {
        System.out.println("  카드로 " + amount + "원을 결제합니다.");
    }
}

class CashPayment implements Payable {
    @Override
    public void pay(int amount) {
        System.out.println("  현금으로 " + amount + "원을 냅니다.");
    }
}

class Box<T> {
    private T item;

    public void put(T item) {
        this.item = item;
    }

    public T get() {
        return item;
    }
}

public class Main {
    static void lesson1Interface() {
        /*
         * 인터페이스는 "해야 할 약속"입니다.
         * 자판기 버튼에 '결제 가능'이라고 적혀 있으면,
         * 카드든 현금이든 결제 규칙만 맞추면 됩니다.
         */
        System.out.println("[레슨 1] 인터페이스");
        Payable[] methods = {new CardPayment(), new CashPayment()};
        for (Payable method : methods) {
            method.pay(1500);
        }
        System.out.println();
    }

    static void lesson2Generic() {
        /*
         * 제네릭은 "상자 모양은 같은데 내용물 타입만 바꾸는 기술"입니다.
         * 장난감 상자, 책 상자, 과일 상자를 각각 만들지 않고
         * Box<T> 하나로 다양한 타입을 담을 수 있습니다.
         */
        Box<String> nameBox = new Box<>();
        nameBox.put("연필");

        Box<Integer> numberBox = new Box<>();
        numberBox.put(7);

        System.out.println("[레슨 2] 제네릭");
        System.out.println("  문자열 상자: " + nameBox.get());
        System.out.println("  숫자 상자  : " + numberBox.get());
        System.out.println();
    }

    static void lesson3WhyUseful() {
        System.out.println("[레슨 3] 왜 유용할까?");
        System.out.println("  인터페이스는 역할을 통일해 주고, 제네릭은 타입 실수를 줄여 줍니다.");
        System.out.println("  즉, 설계도는 단단해지고 코드 재사용은 쉬워집니다.");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 07단계 : 인터페이스와 제네릭");
        System.out.println("============================================================");
        System.out.println();

        lesson1Interface();
        lesson2Generic();
        lesson3WhyUseful();
    }
}
''',
    )

    write(
        "java-learning/08_exceptions_file_io/Main.java",
        r'''
/*
===============================================================================
  Java 학습 08단계: 예외와 파일 입출력
===============================================================================
*/

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class Main {
    static void lesson1ExceptionMindset() {
        /*
         * 예외는 "프로그램이 예상 못 한 돌부리에 걸린 상황"입니다.
         * 길을 걷다가 계단이 갑자기 나타나면 발을 조심해야 하듯,
         * 파일이 없거나 권한이 없을 때도 대비 코드가 필요합니다.
         */
        System.out.println("[레슨 1] 예외를 왜 배울까?");
        System.out.println("  실패 가능성을 미리 적어 두면 프로그램이 덜 갑자기 멈춥니다.");
        System.out.println();
    }

    static void lesson2TryCatch() {
        System.out.println("[레슨 2] try-catch");
        try {
            int result = 10 / 2;
            System.out.println("  정상 계산 결과: " + result);
            int crash = 10 / 0;
            System.out.println(crash);
        } catch (ArithmeticException e) {
            System.out.println("  0으로 나눌 수 없어서 예외가 발생했습니다.");
            System.out.println("  메시지: " + e.getMessage());
        }
        System.out.println();
    }

    static void lesson3FileReadWrite() {
        Path path = Path.of("java-learning", "08_exceptions_file_io", "sample.txt");
        System.out.println("[레슨 3] 파일 읽기와 쓰기");
        try {
            Files.writeString(path, "사과\n바나나\n포도\n");
            List<String> lines = Files.readAllLines(path);
            for (String line : lines) {
                System.out.println("  읽은 줄: " + line);
            }
        } catch (IOException e) {
            System.out.println("  파일 처리 중 문제가 생겼습니다: " + e.getMessage());
        }
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 08단계 : 예외와 파일 입출력");
        System.out.println("============================================================");
        System.out.println();

        lesson1ExceptionMindset();
        lesson2TryCatch();
        lesson3FileReadWrite();
    }
}
''',
    )

    write(
        "java-learning/09_streams_lambda/Main.java",
        r'''
/*
===============================================================================
  Java 학습 09단계: 스트림과 람다
===============================================================================
*/

import java.util.Arrays;
import java.util.List;

public class Main {
    static void lesson1Lambda() {
        /*
         * 람다는 "짧게 건네는 작은 행동 조각"입니다.
         * "이 학생들 중 점수가 80 이상인 사람만 골라 줘" 같은 부탁을
         * 함수처럼 짧게 적을 수 있습니다.
         */
        List<Integer> scores = Arrays.asList(55, 72, 88, 91, 64);

        System.out.println("[레슨 1] 람다 기본");
        scores.forEach(score -> System.out.println("  점수: " + score));
        System.out.println();
    }

    static void lesson2StreamFilterMap() {
        List<Integer> scores = Arrays.asList(55, 72, 88, 91, 64);

        System.out.println("[레슨 2] filter 와 map");
        scores.stream()
            .filter(score -> score >= 70)
            .map(score -> "통과 점수: " + score)
            .forEach(text -> System.out.println("  " + text));
        System.out.println();
    }

    static void lesson3WhyPipeline() {
        System.out.println("[레슨 3] 파이프라인 비유");
        System.out.println("  세탁 공장처럼 생각하면 쉽습니다.");
        System.out.println("  빨래를 넣고 -> 고르고 -> 정리해서 -> 결과를 꺼내는 흐름입니다.");
        System.out.println("  Stream 도 데이터에 여러 작업을 순서대로 붙입니다.");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 09단계 : 스트림과 람다");
        System.out.println("============================================================");
        System.out.println();

        lesson1Lambda();
        lesson2StreamFilterMap();
        lesson3WhyPipeline();
    }
}
''',
    )

    write(
        "java-learning/10_modern_java/Main.java",
        r'''
/*
===============================================================================
  Java 학습 10단계: 모던 자바
===============================================================================
*/

record Student(String name, int score) {}

public class Main {
    static void lesson1Var() {
        /*
         * var 는 "타입을 생략해도 컴파일러가 눈치채는 기능"입니다.
         * 하지만 아무 때나 짧게 쓰는 것이 좋은 것은 아닙니다.
         * 너무 복잡한 코드에서 var 를 남발하면 오히려 읽기 어려워집니다.
         */
        var name = "민수";
        var score = 88;

        System.out.println("[레슨 1] var");
        System.out.println("  이름: " + name);
        System.out.println("  점수: " + score);
        System.out.println();
    }

    static void lesson2Record() {
        Student student = new Student("지우", 95);

        System.out.println("[레슨 2] record");
        System.out.println("  record 는 데이터를 담는 상자를 간단히 만드는 문법입니다.");
        System.out.println("  " + student.name() + " 학생의 점수는 " + student.score() + "점입니다.");
        System.out.println();
    }

    static void lesson3SwitchExpression() {
        int level = 2;
        String text = switch (level) {
            case 1 -> "입문";
            case 2 -> "기초";
            case 3 -> "심화";
            default -> "알 수 없음";
        };

        System.out.println("[레슨 3] switch expression");
        System.out.println("  레벨 " + level + " 는 " + text + " 단계입니다.");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 10단계 : 모던 자바");
        System.out.println("============================================================");
        System.out.println();

        lesson1Var();
        lesson2Record();
        lesson3SwitchExpression();
    }
}
''',
    )

    write(
        "java-learning/11_debugging/Main.java",
        r'''
/*
===============================================================================
  Java 학습 11단계: 디버깅
===============================================================================
*/

public class Main {
    static int divideCandy(int candy, int childCount) {
        return candy / childCount;
    }

    static void lesson1BugStory() {
        /*
         * 디버깅은 "틀린 답을 맞히는 추리 게임"이 아닙니다.
         * 값이 언제, 어디서, 왜 바뀌었는지를 따라가는 관찰 훈련입니다.
         */
        System.out.println("[레슨 1] 디버깅의 핵심");
        System.out.println("  추측하지 말고, 값을 하나씩 확인해야 합니다.");
        System.out.println();
    }

    static void lesson2TraceValue() {
        int candy = 12;
        int childCount = 3;
        int result = divideCandy(candy, childCount);

        System.out.println("[레슨 2] 값 추적하기");
        System.out.println("  candy      = " + candy);
        System.out.println("  childCount = " + childCount);
        System.out.println("  result     = " + result);
        System.out.println();
    }

    static void lesson3FailCase() {
        System.out.println("[레슨 3] 실패 사례 보기");
        try {
            int result = divideCandy(12, 0);
            System.out.println(result);
        } catch (ArithmeticException e) {
            System.out.println("  childCount 가 0 이면 나눗셈이 실패합니다.");
            System.out.println("  즉, 디버깅은 '입력 조건'도 같이 봐야 합니다.");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 11단계 : 디버깅");
        System.out.println("============================================================");
        System.out.println();

        lesson1BugStory();
        lesson2TraceValue();
        lesson3FailCase();
    }
}
''',
    )

    write(
        "java-learning/12_build_tools/Main.java",
        r'''
/*
===============================================================================
  Java 학습 12단계: 빌드 도구
===============================================================================
*/

public class Main {
    static void lesson1WhatIsBuild() {
        /*
         * 빌드는 "재료를 모아 완성품을 만드는 과정"입니다.
         * 밀가루, 설탕, 달걀을 섞어 케이크를 굽듯,
         * 소스 코드, 라이브러리, 설정을 모아 실행 가능한 결과물을 만듭니다.
         */
        System.out.println("[레슨 1] 빌드란?");
        System.out.println("  컴파일, 테스트, 패키징을 하나의 흐름으로 묶는 작업입니다.");
        System.out.println();
    }

    static void lesson2MavenVsGradle() {
        System.out.println("[레슨 2] Maven 과 Gradle");
        System.out.println("  Maven  : 규칙이 분명한 조립 설명서에 가깝습니다.");
        System.out.println("  Gradle : 조금 더 유연한 자동화 공장에 가깝습니다.");
        System.out.println();
    }

    static void lesson3DependencyIdea() {
        System.out.println("[레슨 3] 의존성 관리");
        System.out.println("  라이브러리는 내가 직접 만들지 않은 부품입니다.");
        System.out.println("  빌드 도구는 필요한 부품 버전을 적고 자동으로 가져오게 도와줍니다.");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 12단계 : 빌드 도구");
        System.out.println("============================================================");
        System.out.println();

        lesson1WhatIsBuild();
        lesson2MavenVsGradle();
        lesson3DependencyIdea();
    }
}
''',
    )

    write(
        "java-learning/13_design_patterns/Main.java",
        r'''
/*
===============================================================================
  Java 학습 13단계: 디자인 패턴
===============================================================================
*/

interface MessageSender {
    void send(String message);
}

class EmailSender implements MessageSender {
    @Override
    public void send(String message) {
        System.out.println("  이메일 발송: " + message);
    }
}

class SmsSender implements MessageSender {
    @Override
    public void send(String message) {
        System.out.println("  문자 발송: " + message);
    }
}

class NotificationService {
    private final MessageSender sender;

    NotificationService(MessageSender sender) {
        this.sender = sender;
    }

    void notify(String message) {
        sender.send(message);
    }
}

public class Main {
    static void lesson1PatternMindset() {
        /*
         * 디자인 패턴은 "정답 암기장"이 아닙니다.
         * 자주 나오는 문제를 풀기 위한 검증된 생각의 틀입니다.
         * 즉, 이름을 외우는 것보다 "왜 이런 모양을 쓰는가"가 중요합니다.
         */
        System.out.println("[레슨 1] 패턴을 왜 배울까?");
        System.out.println("  자주 만나는 설계 문제를 더 빨리, 덜 흔들리며 해결할 수 있습니다.");
        System.out.println();
    }

    static void lesson2StrategyPattern() {
        NotificationService emailService = new NotificationService(new EmailSender());
        NotificationService smsService = new NotificationService(new SmsSender());

        System.out.println("[레슨 2] Strategy 패턴 느낌");
        emailService.notify("시험 결과가 등록되었습니다.");
        smsService.notify("오늘의 숙제를 확인하세요.");
        System.out.println();
    }

    static void lesson3Analogy() {
        System.out.println("[레슨 3] 비유");
        System.out.println("  같은 편지라도 우체국, 택배, 퀵서비스처럼 보내는 방법이 달라질 수 있습니다.");
        System.out.println("  서비스는 '보낸다'는 큰 목적만 알고, 실제 방식은 전략 객체가 담당합니다.");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Java 13단계 : 디자인 패턴");
        System.out.println("============================================================");
        System.out.println();

        lesson1PatternMindset();
        lesson2StrategyPattern();
        lesson3Analogy();
    }
}
''',
    )

    write(
        "go-learning/04_arrays_slices_maps/main.go",
        r'''
/*
===============================================================================
  Go 학습 04단계: 배열, 슬라이스, 맵
===============================================================================
*/

package main

import "fmt"

func lesson1Array() {
    /*
       배열은 칸 수가 딱 정해진 도시락입니다.
       3칸 도시락이면 3칸만 쓸 수 있고, 갑자기 4칸으로 늘어나지 않습니다.
    */
    scores := [3]int{70, 80, 90}
    fmt.Println("[레슨 1] 배열")
    fmt.Println("  배열 전체:", scores)
    fmt.Println("  첫 번째 점수:", scores[0])
    fmt.Println()
}

func lesson2Slice() {
    /*
       슬라이스는 배열보다 더 유연한 접시라고 생각하면 쉽습니다.
       담긴 양에 따라 조금씩 늘어나거나 줄어드는 느낌입니다.
    */
    fruits := []string{"사과", "바나나"}
    fruits = append(fruits, "포도")

    fmt.Println("[레슨 2] 슬라이스")
    fmt.Println("  과일 목록:", fruits)
    fmt.Println("  길이:", len(fruits), "용량:", cap(fruits))
    fmt.Println()
}

func lesson3Map() {
    studentScores := map[string]int{
        "민수": 82,
        "지우": 95,
    }

    fmt.Println("[레슨 3] 맵")
    fmt.Println("  민수 점수:", studentScores["민수"])

    score, exists := studentScores["서연"]
    fmt.Println("  서연 키 존재?", exists, "값:", score)
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 04단계 : 배열, 슬라이스, 맵")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Array()
    lesson2Slice()
    lesson3Map()
}
''',
    )

    write(
        "go-learning/05_structs_methods/main.go",
        r'''
/*
===============================================================================
  Go 학습 05단계: 구조체와 메서드
===============================================================================
*/

package main

import "fmt"

type Student struct {
    Name  string
    Score int
}

func (s Student) PrintReport() {
    result := "복습 필요"
    if s.Score >= 70 {
        result = "통과"
    }

    fmt.Println("  이름:", s.Name)
    fmt.Println("  점수:", s.Score)
    fmt.Println("  결과:", result)
}

func lesson1Struct() {
    /*
       구조체는 관련 있는 값을 한 상자에 묶는 도구입니다.
       학생 이름은 여기, 점수는 저기 흩어 놓으면 관리가 어렵습니다.
       그래서 Student 라는 한 묶음으로 보관합니다.
    */
    student := Student{Name: "민수", Score: 84}

    fmt.Println("[레슨 1] 구조체")
    fmt.Println("  Student 상자 안에 Name, Score 가 함께 들어 있습니다.")
    student.PrintReport()
    fmt.Println()
}

func lesson2Method() {
    student := Student{Name: "지우", Score: 97}

    fmt.Println("[레슨 2] 메서드")
    fmt.Println("  메서드는 구조체가 가진 '전용 기능 버튼'처럼 생각하면 됩니다.")
    student.PrintReport()
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 05단계 : 구조체와 메서드")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Struct()
    lesson2Method()
}
''',
    )

    write(
        "go-learning/06_interfaces/main.go",
        r'''
/*
===============================================================================
  Go 학습 06단계: 인터페이스
===============================================================================
*/

package main

import "fmt"

type Speaker interface {
    Speak() string
}

type Dog struct{}
type Cat struct{}

func (Dog) Speak() string { return "멍멍" }
func (Cat) Speak() string { return "야옹" }

func printSound(s Speaker) {
    fmt.Println("  동물 소리:", s.Speak())
}

func lesson1Concept() {
    /*
       인터페이스는 "무엇을 할 수 있는가"를 적는 약속장입니다.
       누구든 Speak() 라는 약속만 지키면 Speaker 로 다룰 수 있습니다.
    */
    fmt.Println("[레슨 1] 인터페이스란?")
    fmt.Println("  모양이 아니라 행동 규칙으로 묶습니다.")
    fmt.Println()
}

func lesson2Usage() {
    fmt.Println("[레슨 2] 사용 예제")
    printSound(Dog{})
    printSound(Cat{})
    fmt.Println()
}

func lesson3Analogy() {
    fmt.Println("[레슨 3] 비유")
    fmt.Println("  리모컨은 TV 회사가 달라도 '전원 켜기' 버튼 역할이 중요합니다.")
    fmt.Println("  Go 인터페이스도 구체 타입보다 가능한 행동을 중심으로 생각합니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 06단계 : 인터페이스")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Concept()
    lesson2Usage()
    lesson3Analogy()
}
''',
    )

    write(
        "go-learning/07_goroutines_channels/main.go",
        r'''
/*
===============================================================================
  Go 학습 07단계: 고루틴과 채널
===============================================================================
*/

package main

import (
    "fmt"
    "time"
)

func boilWater(done chan string) {
    time.Sleep(300 * time.Millisecond)
    done <- "물을 끓였습니다."
}

func toastBread(done chan string) {
    time.Sleep(100 * time.Millisecond)
    done <- "빵을 구웠습니다."
}

func lesson1Goroutine() {
    /*
       고루틴은 "작업을 따로 출발시키는 아주 가벼운 일꾼"입니다.
       혼자 요리하면 물 끓이기 끝난 뒤에 빵을 굽지만,
       동시에 시작하면 더 빨리 아침을 준비할 수 있습니다.
    */
    fmt.Println("[레슨 1] 고루틴")
    fmt.Println("  go 키워드는 함수를 새 작업 흐름으로 보냅니다.")
    fmt.Println()
}

func lesson2Channel() {
    done := make(chan string)

    fmt.Println("[레슨 2] 채널")
    go boilWater(done)
    go toastBread(done)

    first := <-done
    second := <-done

    fmt.Println("  첫 번째 완료:", first)
    fmt.Println("  두 번째 완료:", second)
    fmt.Println()
}

func lesson3WhyChannelMatters() {
    fmt.Println("[레슨 3] 왜 채널이 중요할까?")
    fmt.Println("  여러 고루틴이 같은 메모장을 마구 덮어쓰면 충돌이 납니다.")
    fmt.Println("  채널은 '말을 건네는 창구'라서 작업 사이의 전달을 더 안전하게 만듭니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 07단계 : 고루틴과 채널")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Goroutine()
    lesson2Channel()
    lesson3WhyChannelMatters()
}
''',
    )

    write(
        "go-learning/08_error_handling/main.go",
        r'''
/*
===============================================================================
  Go 학습 08단계: 에러 처리
===============================================================================
*/

package main

import (
    "errors"
    "fmt"
)

func divide(a int, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("0으로 나눌 수 없습니다")
    }
    return a / b, nil
}

func lesson1WhyError() {
    /*
       Go 는 에러를 숨기기보다 눈앞에 꺼내 놓는 스타일입니다.
       교실에서 문제를 틀렸을 때 빨간 표시를 바로 보는 것과 비슷합니다.
       불편해 보여도 어디서 문제가 났는지 빨리 찾게 도와줍니다.
    */
    fmt.Println("[레슨 1] 에러 처리 철학")
    fmt.Println("  Go 는 예외를 화려하게 숨기기보다, 반환값으로 분명하게 알려 줍니다.")
    fmt.Println()
}

func lesson2CheckError() {
    fmt.Println("[레슨 2] 에러 확인")
    result, err := divide(10, 2)
    if err != nil {
        fmt.Println("  실패:", err)
    } else {
        fmt.Println("  성공 결과:", result)
    }

    result, err = divide(10, 0)
    if err != nil {
        fmt.Println("  실패:", err)
    } else {
        fmt.Println("  성공 결과:", result)
    }
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 08단계 : 에러 처리")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1WhyError()
    lesson2CheckError()
}
''',
    )

    write(
        "go-learning/09_packages_modules/main.go",
        r'''
/*
===============================================================================
  Go 학습 09단계: 패키지와 모듈
===============================================================================
*/

package main

import "fmt"

func lesson1Package() {
    /*
       패키지는 서랍입니다.
       양말, 셔츠, 바지를 한 서랍에 다 섞으면 찾기 힘들듯,
       관련 코드를 기능별로 나눠 보관해야 프로젝트가 커져도 버티기 쉽습니다.
    */
    fmt.Println("[레슨 1] 패키지")
    fmt.Println("  비슷한 역할의 코드를 같은 폴더와 같은 이름으로 묶습니다.")
    fmt.Println()
}

func lesson2Module() {
    fmt.Println("[레슨 2] 모듈")
    fmt.Println("  모듈은 여러 패키지를 감싸는 큰 프로젝트 단위입니다.")
    fmt.Println("  go.mod 파일은 '이 프로젝트의 이름과 필요한 부품 목록' 같은 역할을 합니다.")
    fmt.Println()
}

func lesson3ImportMindset() {
    fmt.Println("[레슨 3] import 를 어떻게 볼까?")
    fmt.Println("  import 는 이미 만들어 둔 도구 상자를 빌려오는 문장입니다.")
    fmt.Println("  fmt 를 import 했기 때문에 Println 같은 기능을 쓸 수 있습니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 09단계 : 패키지와 모듈")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Package()
    lesson2Module()
    lesson3ImportMindset()
}
''',
    )

    write(
        "go-learning/10_standard_library/main.go",
        r'''
/*
===============================================================================
  Go 학습 10단계: 표준 라이브러리
===============================================================================
*/

package main

import (
    "fmt"
    "strings"
    "time"
)

func lesson1Strings() {
    text := "go is simple"

    fmt.Println("[레슨 1] strings 패키지")
    fmt.Println("  대문자 변환:", strings.ToUpper(text))
    fmt.Println("  포함 여부  :", strings.Contains(text, "simple"))
    fmt.Println()
}

func lesson2Time() {
    now := time.Now()

    fmt.Println("[레슨 2] time 패키지")
    fmt.Println("  현재 시각:", now.Format("2006-01-02 15:04:05"))
    fmt.Println("  2시간 뒤 :", now.Add(2*time.Hour).Format("15:04:05"))
    fmt.Println()
}

func lesson3WhyLibrary() {
    /*
       표준 라이브러리는 학교 기본 준비물 세트와 비슷합니다.
       자, 지우개, 공책을 처음부터 매번 만들지 않듯
       문자열 처리, 시간 처리 같은 기본 기능은 이미 준비돼 있습니다.
    */
    fmt.Println("[레슨 3] 왜 표준 라이브러리가 중요할까?")
    fmt.Println("  기본 도구가 튼튼하면 애플리케이션 로직에 더 집중할 수 있습니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 10단계 : 표준 라이브러리")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Strings()
    lesson2Time()
    lesson3WhyLibrary()
}
''',
    )

    write(
        "go-learning/11_debugging/main.go",
        r'''
/*
===============================================================================
  Go 학습 11단계: 디버깅
===============================================================================
*/

package main

import "fmt"

func average(scores []int) int {
    total := 0
    for _, score := range scores {
        total += score
    }
    return total / len(scores)
}

func lesson1Trace() {
    scores := []int{80, 90, 70}
    fmt.Println("[레슨 1] 값 따라가기")
    fmt.Println("  입력:", scores)
    fmt.Println("  평균:", average(scores))
    fmt.Println()
}

func lesson2BugPoint() {
    /*
       디버깅은 "여기쯤 틀렸겠지?"가 아니라
       "실제로 어떤 값이 들어왔는가?"를 보는 일입니다.
       특히 길이가 0인 슬라이스는 나누기에서 문제를 만들 수 있습니다.
    */
    fmt.Println("[레슨 2] 문제 지점 찾기")
    fmt.Println("  빈 슬라이스가 들어오면 len(scores) 가 0 이라서 위험합니다.")
    fmt.Println("  즉, 디버깅은 정상 케이스뿐 아니라 빈 값도 확인해야 합니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 11단계 : 디버깅")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Trace()
    lesson2BugPoint()
}
''',
    )

    write(
        "go-learning/12_testing/main.go",
        r'''
/*
===============================================================================
  Go 학습 12단계: 테스트
===============================================================================
*/

package main

import "fmt"

func canPass(score int) bool {
    return score >= 70
}

func lesson1WhyTest() {
    /*
       테스트는 "코드를 믿기 전에 확인하는 체크리스트"입니다.
       다리를 건너기 전에 튼튼한지 흔들어 보는 것과 비슷합니다.
    */
    fmt.Println("[레슨 1] 테스트가 왜 필요할까?")
    fmt.Println("  코드를 수정한 뒤에도 예전 기능이 여전히 맞는지 확인할 수 있습니다.")
    fmt.Println()
}

func lesson2ManualCases() {
    cases := []int{50, 70, 95}

    fmt.Println("[레슨 2] 테스트 케이스 생각하기")
    for _, score := range cases {
        fmt.Printf("  점수 %d -> 통과 여부 %v\n", score, canPass(score))
    }
    fmt.Println("  특히 경계값 70점은 꼭 확인해야 합니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 12단계 : 테스트")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1WhyTest()
    lesson2ManualCases()
}
''',
    )

    write(
        "csharp-learning/08_exceptions_file_io/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 08단계: 예외와 파일 입출력
===============================================================================
*/

using System;
using System.IO;
using System.Text;

namespace Lesson08
{
    class Program
    {
        static void Lesson1Exception()
        {
            /*
             * 예외는 프로그램이 "앗, 이 상황은 예상 밖인데?"라고 말하는 순간입니다.
             * 파일이 없거나, 0으로 나누거나, 권한이 없을 때처럼
             * 평소 흐름이 깨지는 경우를 안전하게 다루기 위해 필요합니다.
             */
            Console.WriteLine("[레슨 1] 예외");
            try
            {
                int result = 10 / 0;
                Console.WriteLine(result);
            }
            catch (DivideByZeroException ex)
            {
                Console.WriteLine("  0으로 나눌 수 없습니다.");
                Console.WriteLine("  예외 메시지: " + ex.Message);
            }
            Console.WriteLine();
        }

        static void Lesson2FileIO()
        {
            string path = Path.Combine("csharp-learning", "08_exceptions_file_io", "sample.txt");

            Console.WriteLine("[레슨 2] 파일 입출력");
            File.WriteAllText(path, "사과\r\n바나나\r\n포도\r\n", Encoding.UTF8);
            string[] lines = File.ReadAllLines(path, Encoding.UTF8);

            foreach (string line in lines)
            {
                Console.WriteLine("  읽은 줄: " + line);
            }
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 08단계 : 예외와 파일 입출력");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1Exception();
            Lesson2FileIO();
        }
    }
}
''',
    )

    write(
        "csharp-learning/09_linq_lambda/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 09단계: LINQ와 람다
===============================================================================
*/

using System;
using System.Linq;
using System.Text;

namespace Lesson09
{
    class Program
    {
        static void Lesson1Lambda()
        {
            int[] scores = { 55, 71, 88, 93, 64 };

            /*
             * 람다는 "짧게 건네는 행동 설명서"입니다.
             * "70점 이상만 골라 줘" 같은 규칙을 함수처럼 짧게 적을 수 있습니다.
             */
            Console.WriteLine("[레슨 1] 람다");
            foreach (int score in scores.Where(score => score >= 70))
            {
                Console.WriteLine("  통과 후보: " + score);
            }
            Console.WriteLine();
        }

        static void Lesson2LinqFlow()
        {
            string[] names = { "민수", "지우", "서연", "도윤" };
            var shortNames = names
                .Where(name => name.Length <= 2)
                .Select(name => $"{name} 학생");

            Console.WriteLine("[레슨 2] LINQ 흐름");
            foreach (string item in shortNames)
            {
                Console.WriteLine("  " + item);
            }
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 09단계 : LINQ와 람다");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1Lambda();
            Lesson2LinqFlow();
        }
    }
}
''',
    )

    write(
        "csharp-learning/10_modern_csharp/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 10단계: 모던 C#
===============================================================================
*/

using System;
using System.Text;

namespace Lesson10
{
    record Student(string Name, int Score);

    class Program
    {
        static void Lesson1VarAndInterpolation()
        {
            var name = "민수";
            var score = 88;

            Console.WriteLine("[레슨 1] var 와 문자열 보간");
            Console.WriteLine($"  {name} 학생의 점수는 {score}점입니다.");
            Console.WriteLine();
        }

        static void Lesson2Record()
        {
            /*
             * record 는 "데이터 중심 객체를 간단히 만드는 문법"입니다.
             * 학생 정보처럼 값 비교가 중요한 데이터에 잘 어울립니다.
             */
            var student = new Student("지우", 95);

            Console.WriteLine("[레슨 2] record");
            Console.WriteLine($"  이름: {student.Name}, 점수: {student.Score}");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 10단계 : 모던 C#");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1VarAndInterpolation();
            Lesson2Record();
        }
    }
}
''',
    )

    write(
        "csharp-learning/11_debugging/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 11단계: 디버깅
===============================================================================
*/

using System;
using System.Text;

namespace Lesson11
{
    class Program
    {
        static int Average(int[] values)
        {
            int total = 0;
            foreach (int value in values)
            {
                total += value;
            }
            return total / values.Length;
        }

        static void Lesson1Trace()
        {
            int[] scores = { 80, 90, 70 };
            Console.WriteLine("[레슨 1] 값 추적");
            Console.WriteLine("  입력 길이: " + scores.Length);
            Console.WriteLine("  평균: " + Average(scores));
            Console.WriteLine();
        }

        static void Lesson2FindRisk()
        {
            /*
             * 디버깅은 추측보다 확인입니다.
             * 빈 배열이 들어오면 values.Length 가 0 이라서
             * 나누기 과정에서 예외가 날 수 있다는 점을 찾아야 합니다.
             */
            Console.WriteLine("[레슨 2] 위험 지점 찾기");
            Console.WriteLine("  빈 배열을 넣으면 0으로 나누게 될 수 있습니다.");
            Console.WriteLine("  즉, 입력 데이터의 경계값을 먼저 확인해야 합니다.");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 11단계 : 디버깅");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1Trace();
            Lesson2FindRisk();
        }
    }
}
''',
    )

    write(
        "csharp-learning/12_nuget_libraries/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 12단계: NuGet과 라이브러리
===============================================================================
*/

using System;
using System.Text;

namespace Lesson12
{
    class Program
    {
        static void Lesson1Library()
        {
            /*
             * 라이브러리는 "내가 직접 다 만들지 않아도 되는 부품 상자"입니다.
             * 자동차를 만들 때 바퀴까지 매번 처음부터 만들지 않듯,
             * 검증된 기능을 가져와 조립하는 것이 현실적인 개발입니다.
             */
            Console.WriteLine("[레슨 1] 라이브러리");
            Console.WriteLine("  자주 쓰는 기능을 재사용하면 시간과 실수를 줄일 수 있습니다.");
            Console.WriteLine();
        }

        static void Lesson2NuGet()
        {
            Console.WriteLine("[레슨 2] NuGet");
            Console.WriteLine("  NuGet 은 C# 프로젝트의 패키지 매니저입니다.");
            Console.WriteLine("  필요한 라이브러리 이름과 버전을 적고 받아오는 도구라고 보면 됩니다.");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 12단계 : NuGet과 라이브러리");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1Library();
            Lesson2NuGet();
        }
    }
}
''',
    )

    write(
        "csharp-learning/13_design_patterns/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 13단계: 디자인 패턴
===============================================================================
*/

using System;
using System.Text;

namespace Lesson13
{
    interface IDiscountStrategy
    {
        int Apply(int price);
    }

    class NoDiscount : IDiscountStrategy
    {
        public int Apply(int price) => price;
    }

    class StudentDiscount : IDiscountStrategy
    {
        public int Apply(int price) => price - 1000;
    }

    class Cashier
    {
        private readonly IDiscountStrategy _strategy;

        public Cashier(IDiscountStrategy strategy)
        {
            _strategy = strategy;
        }

        public void PrintPrice(int price)
        {
            Console.WriteLine("  원래 가격: " + price);
            Console.WriteLine("  할인 적용: " + _strategy.Apply(price));
        }
    }

    class Program
    {
        static void Lesson1Pattern()
        {
            /*
             * 패턴은 이름 외우기 대회가 아닙니다.
             * 자주 나오는 문제에서 "이럴 때 이런 구조가 잘 먹힌다"는 경험 모음입니다.
             */
            Console.WriteLine("[레슨 1] 디자인 패턴 관점");
            Console.WriteLine("  설계를 고정된 답으로 보지 말고, 문제를 푸는 틀로 봐야 합니다.");
            Console.WriteLine();
        }

        static void Lesson2Strategy()
        {
            Console.WriteLine("[레슨 2] Strategy 예제");
            new Cashier(new NoDiscount()).PrintPrice(5000);
            new Cashier(new StudentDiscount()).PrintPrice(5000);
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 13단계 : 디자인 패턴");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1Pattern();
            Lesson2Strategy();
        }
    }
}
''',
    )

    write(
        "csharp-learning/15_networking/Program.cs",
        r'''
/*
===============================================================================
  C# 학습 15단계: 네트워킹
===============================================================================
*/

using System;
using System.Text;

namespace Lesson15
{
    class Program
    {
        static void Lesson1RequestResponse()
        {
            /*
             * 네트워크 통신은 편지를 보내고 답장을 받는 흐름과 비슷합니다.
             * 클라이언트가 요청을 보내고, 서버가 응답을 돌려줍니다.
             */
            Console.WriteLine("[레슨 1] 요청과 응답");
            Console.WriteLine("  클라이언트 -> 서버 : 요청");
            Console.WriteLine("  서버 -> 클라이언트 : 응답");
            Console.WriteLine();
        }

        static void Lesson2IpPort()
        {
            Console.WriteLine("[레슨 2] IP 와 Port");
            Console.WriteLine("  IP   : 건물 주소");
            Console.WriteLine("  Port : 건물 안의 방 번호");
            Console.WriteLine("  서버 안에서도 어떤 프로그램이 받는지 Port 로 구분합니다.");
            Console.WriteLine();
        }

        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 15단계 : 네트워킹");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Lesson1RequestResponse();
            Lesson2IpPort();
        }
    }
}
''',
    )

    write(
        "rust-learning/05_structs_enums/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 05단계: 구조체와 열거형
// =============================================================================

struct Student {
    name: String,
    score: i32,
}

enum TrafficLight {
    Red,
    Yellow,
    Green,
}

fn lesson1_struct() {
    /*
       구조체는 관련 있는 값을 하나의 상자로 묶는 도구입니다.
       이름과 점수를 따로 흩어 놓지 않고 Student 안에 담으면
       "이 둘은 같은 학생 정보"라는 뜻이 코드에 보입니다.
    */
    let student = Student {
        name: String::from("민수"),
        score: 86,
    };

    println!("[레슨 1] 구조체");
    println!("  이름: {}", student.name);
    println!("  점수: {}", student.score);
    println!();
}

fn lesson2_enum() {
    let light = TrafficLight::Yellow;

    println!("[레슨 2] 열거형");
    match light {
        TrafficLight::Red => println!("  빨간불: 멈춤"),
        TrafficLight::Yellow => println!("  노란불: 곧 바뀜을 주의"),
        TrafficLight::Green => println!("  초록불: 진행"),
    }
    println!();
}

fn lesson3_why_enum() {
    println!("[레슨 3] 왜 enum 이 좋을까?");
    println!("  문자열로 'red', 'yellow', 'green' 을 직접 쓰면 오타가 날 수 있습니다.");
    println!("  enum 은 가능한 경우를 딱 정해 두어 실수를 줄여 줍니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 05단계 : 구조체와 열거형");
    println!("============================================================");
    println!();

    lesson1_struct();
    lesson2_enum();
    lesson3_why_enum();
}
''',
    )

    write(
        "rust-learning/06_traits/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 06단계: 트레이트
// =============================================================================

trait Summary {
    fn summarize(&self) -> String;
}

struct News {
    title: String,
}

struct Chat {
    user: String,
    message: String,
}

impl Summary for News {
    fn summarize(&self) -> String {
        format!("뉴스 요약: {}", self.title)
    }
}

impl Summary for Chat {
    fn summarize(&self) -> String {
        format!("{} 님의 메시지: {}", self.user, self.message)
    }
}

fn print_summary(item: &impl Summary) {
    println!("  {}", item.summarize());
}

fn lesson1_trait() {
    /*
       트레이트는 "이 타입이 할 수 있는 일의 약속"입니다.
       사람마다 직업은 달라도 자기소개를 할 수 있는 것처럼,
       서로 다른 타입이 같은 행동 규칙을 공유할 수 있습니다.
    */
    println!("[레슨 1] 트레이트란?");
    println!("  타입의 모양보다 '가능한 행동'을 중심으로 묶습니다.");
    println!();
}

fn lesson2_usage() {
    let news = News {
        title: String::from("비가 오는 날에는 우산을 챙기세요"),
    };
    let chat = Chat {
        user: String::from("민수"),
        message: String::from("오늘 숙제 뭐였지?"),
    };

    println!("[레슨 2] 사용 예제");
    print_summary(&news);
    print_summary(&chat);
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 06단계 : 트레이트");
    println!("============================================================");
    println!();

    lesson1_trait();
    lesson2_usage();
}
''',
    )

    write(
        "rust-learning/07_collections/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 07단계: 컬렉션
// =============================================================================

use std::collections::HashMap;

fn lesson1_vector() {
    let mut scores = vec![70, 80, 90];
    scores.push(100);

    println!("[레슨 1] Vec");
    println!("  점수 목록: {:?}", scores);
    println!("  첫 번째 값: {}", scores[0]);
    println!();
}

fn lesson2_string() {
    let mut text = String::from("안녕");
    text.push_str(" Rust");

    println!("[레슨 2] String");
    println!("  문자열 결과: {}", text);
    println!("  문자열은 수정 가능한 글자 상자라고 생각하면 됩니다.");
    println!();
}

fn lesson3_hashmap() {
    let mut scores = HashMap::new();
    scores.insert("민수", 82);
    scores.insert("지우", 95);

    println!("[레슨 3] HashMap");
    println!("  민수 점수: {:?}", scores.get("민수"));
    println!("  서연 점수: {:?}", scores.get("서연"));
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 07단계 : 컬렉션");
    println!("============================================================");
    println!();

    lesson1_vector();
    lesson2_string();
    lesson3_hashmap();
}
''',
    )

    write(
        "rust-learning/08_error_handling/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 08단계: 에러 처리
// =============================================================================

fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("0으로 나눌 수 없습니다"))
    } else {
        Ok(a / b)
    }
}

fn lesson1_result() {
    /*
       Rust 는 실패 가능성을 숨기지 않습니다.
       Result 는 "성공 상자"와 "실패 상자" 둘 중 하나를 돌려주는 방식입니다.
       그래서 개발자가 실패 가능성을 억지로 무시하기 어렵습니다.
    */
    println!("[레슨 1] Result");
    match divide(10, 2) {
        Ok(value) => println!("  성공 결과: {}", value),
        Err(message) => println!("  실패 메시지: {}", message),
    }
    println!();
}

fn lesson2_fail_case() {
    println!("[레슨 2] 실패 사례");
    match divide(10, 0) {
        Ok(value) => println!("  성공 결과: {}", value),
        Err(message) => println!("  실패 메시지: {}", message),
    }
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 08단계 : 에러 처리");
    println!("============================================================");
    println!();

    lesson1_result();
    lesson2_fail_case();
}
''',
    )

    write(
        "rust-learning/09_closures_iterators/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 09단계: 클로저와 이터레이터
// =============================================================================

fn lesson1_closure() {
    let add_one = |x: i32| x + 1;

    /*
       클로저는 "짧게 들고 다니는 미니 함수"라고 생각하면 쉽습니다.
       자주 쓰는 작은 규칙을 바로 옆에서 정의해 사용할 수 있습니다.
    */
    println!("[레슨 1] 클로저");
    println!("  5에 1을 더하면 {}", add_one(5));
    println!();
}

fn lesson2_iterator() {
    let scores = vec![55, 72, 88, 91];
    let passed: Vec<i32> = scores
        .into_iter()
        .filter(|score| *score >= 70)
        .collect();

    println!("[레슨 2] 이터레이터");
    println!("  통과 점수들: {:?}", passed);
    println!();
}

fn lesson3_pipeline_analogy() {
    println!("[레슨 3] 비유");
    println!("  공장 컨베이어벨트처럼 데이터를 한 단계씩 처리합니다.");
    println!("  꺼내고, 거르고, 바꾸고, 다시 모으는 흐름이 이터레이터입니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 09단계 : 클로저와 이터레이터");
    println!("============================================================");
    println!();

    lesson1_closure();
    lesson2_iterator();
    lesson3_pipeline_analogy();
}
''',
    )

    write(
        "c-learning/06_memory_management/main.c",
        r'''
/*
===============================================================================
  C 학습 06단계: 메모리 관리
===============================================================================
*/

#include <stdio.h>
#include <stdlib.h>

void lesson1_stack_and_heap(void);
void lesson2_malloc_free(void);
void lesson3_common_mistakes(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 06단계 : 메모리 관리\n");
    printf("============================================================\n\n");

    lesson1_stack_and_heap();
    lesson2_malloc_free();
    lesson3_common_mistakes();
    return 0;
}

void lesson1_stack_and_heap(void) {
    /*
      stack 은 자동 보관함,
      heap 은 직접 빌리고 직접 반납해야 하는 창고라고 생각하면 쉽습니다.
      C 는 이 창고 관리까지 개발자가 챙겨야 합니다.
    */
    int local_value = 10;

    printf("[레슨 1] stack 과 heap\n");
    printf("  local_value 는 함수가 끝나면 자동으로 정리되는 stack 변수입니다: %d\n\n", local_value);
}

void lesson2_malloc_free(void) {
    int* scores = (int*)malloc(sizeof(int) * 3);

    printf("[레슨 2] malloc 과 free\n");
    if (scores == NULL) {
        printf("  메모리 할당 실패\n\n");
        return;
    }

    scores[0] = 80;
    scores[1] = 90;
    scores[2] = 100;

    for (int i = 0; i < 3; i++) {
        printf("  scores[%d] = %d\n", i, scores[i]);
    }

    free(scores);
    printf("  빌린 heap 메모리를 free 로 반납했습니다.\n\n");
}

void lesson3_common_mistakes(void) {
    printf("[레슨 3] 자주 하는 실수\n");
    printf("  1. malloc 후 NULL 확인을 생략합니다.\n");
    printf("  2. free 를 잊어 메모리 누수를 만듭니다.\n");
    printf("  3. free 한 메모리를 다시 사용하려고 합니다.\n\n");
}
''',
    )

    write(
        "c-learning/07_file_io/main.c",
        r'''
/*
===============================================================================
  C 학습 07단계: 파일 입출력
===============================================================================
*/

#include <stdio.h>

void lesson1_write_file(void);
void lesson2_read_file(void);
void lesson3_why_close(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 07단계 : 파일 입출력\n");
    printf("============================================================\n\n");

    lesson1_write_file();
    lesson2_read_file();
    lesson3_why_close();
    return 0;
}

void lesson1_write_file(void) {
    FILE* file = fopen("c-learning/07_file_io/sample.txt", "w");

    printf("[레슨 1] 파일 쓰기\n");
    if (file == NULL) {
        printf("  파일을 열 수 없습니다.\n\n");
        return;
    }

    fprintf(file, "사과\n바나나\n포도\n");
    fclose(file);
    printf("  sample.txt 에 과일 목록을 기록했습니다.\n\n");
}

void lesson2_read_file(void) {
    FILE* file = fopen("c-learning/07_file_io/sample.txt", "r");
    char line[100];

    printf("[레슨 2] 파일 읽기\n");
    if (file == NULL) {
        printf("  파일을 열 수 없습니다.\n\n");
        return;
    }

    while (fgets(line, sizeof(line), file) != NULL) {
        printf("  읽은 줄: %s", line);
    }
    printf("\n");
    fclose(file);
}

void lesson3_why_close(void) {
    /*
      파일은 책을 펼쳐 놓은 것과 비슷합니다.
      다 읽고 덮지 않으면 자원이 계속 잡혀 있을 수 있습니다.
      그래서 fopen 뒤에는 fclose 를 꼭 짝으로 기억해야 합니다.
    */
    printf("[레슨 3] 왜 fclose 가 중요할까?\n");
    printf("  파일 사용이 끝났다는 신호를 운영체제에 알려 줍니다.\n\n");
}
''',
    )

    write(
        "c-learning/08_preprocessor/main.c",
        r'''
/*
===============================================================================
  C 학습 08단계: 전처리기
===============================================================================
*/

#include <stdio.h>

#define PI 3.141592
#define SQUARE(x) ((x) * (x))

void lesson1_define_constant(void);
void lesson2_macro_function(void);
void lesson3_header_thinking(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 08단계 : 전처리기\n");
    printf("============================================================\n\n");

    lesson1_define_constant();
    lesson2_macro_function();
    lesson3_header_thinking();
    return 0;
}

void lesson1_define_constant(void) {
    printf("[레슨 1] #define 상수\n");
    printf("  PI 값: %.6f\n\n", PI);
}

void lesson2_macro_function(void) {
    int number = 5;

    /*
      매크로는 "컴파일 전에 글자를 바꿔 끼우는 치환 규칙"입니다.
      함수처럼 보여도 진짜 함수가 아니라 문장 치환이므로 괄호 실수가 위험합니다.
    */
    printf("[레슨 2] 매크로 함수\n");
    printf("  %d의 제곱은 %d 입니다.\n\n", number, SQUARE(number));
}

void lesson3_header_thinking(void) {
    printf("[레슨 3] 헤더 파일을 왜 나눌까?\n");
    printf("  선언을 모아 두면 여러 .c 파일이 같은 약속을 공유할 수 있습니다.\n");
    printf("  즉, 전처리기는 여러 파일을 연결하는 준비 단계 역할도 합니다.\n\n");
}
''',
    )

    write(
        "c-learning/09_strings/main.c",
        r'''
/*
===============================================================================
  C 학습 09단계: 문자열
===============================================================================
*/

#include <stdio.h>
#include <string.h>

void lesson1_char_array(void);
void lesson2_string_functions(void);
void lesson3_null_character(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 09단계 : 문자열\n");
    printf("============================================================\n\n");

    lesson1_char_array();
    lesson2_string_functions();
    lesson3_null_character();
    return 0;
}

void lesson1_char_array(void) {
    char name[] = "민수";

    printf("[레슨 1] 문자열은 char 배열\n");
    printf("  name = %s\n", name);
    printf("  문자의 개수처럼 보여도 실제로는 여러 칸의 배열입니다.\n\n");
}

void lesson2_string_functions(void) {
    char text[50] = "사과";
    strcat(text, " 주스");

    printf("[레슨 2] 문자열 함수\n");
    printf("  이어 붙인 결과: %s\n", text);
    printf("  길이: %u\n\n", (unsigned)strlen(text));
}

void lesson3_null_character(void) {
    /*
      C 문자열 끝에는 '\0' 이라는 종료 표시가 숨어 있습니다.
      책 끝에 마지막 페이지 표시가 없으면 어디서 끝났는지 모르듯,
      컴퓨터도 '\0' 을 만나야 문자열의 끝을 압니다.
    */
    printf("[레슨 3] 널 문자\n");
    printf("  문자열 끝의 '\\0' 이 없으면 쓰레기 값까지 읽을 수 있습니다.\n\n");
}
''',
    )

    write(
        "dart-learning/05_oop_basics/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 05단계: OOP 기초
===============================================================================
*/

class Student {
  String name;
  int score;

  Student(this.name, this.score);

  void printReport() {
    final result = score >= 70 ? '통과' : '복습 필요';
    print('  이름: $name');
    print('  점수: $score');
    print('  결과: $result');
  }
}

void lesson1Class() {
  /*
     클래스는 설계도이고, 객체는 그 설계도로 만든 실제 물건입니다.
     붕어빵 틀은 클래스, 그 틀로 구운 붕어빵은 객체라고 보면 쉽습니다.
  */
  final student = Student('민수', 84);

  print('[레슨 1] 클래스와 객체');
  student.printReport();
  print('');
}

void lesson2FieldMethod() {
  final student = Student('지우', 95);

  print('[레슨 2] 필드와 메서드');
  print('  field 는 데이터, method 는 행동입니다.');
  student.printReport();
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 05단계 : OOP 기초');
  print('============================================================');
  print('');

  lesson1Class();
  lesson2FieldMethod();
}
''',
    )

    write(
        "dart-learning/06_inheritance_mixins/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 06단계: 상속과 믹스인
===============================================================================
*/

class Animal {
  final String name;

  Animal(this.name);

  void introduce() {
    print('  저는 $name 입니다.');
  }
}

mixin JumpMixin {
  void jump() {
    print('  폴짝! 점프 기능은 mixin 으로 끼워 넣었습니다.');
  }
}

class Dog extends Animal with JumpMixin {
  Dog(super.name);

  void bark() {
    print('  멍멍!');
  }
}

void lesson1Inheritance() {
  /*
     상속은 공통 기능을 부모에게서 물려받는 것입니다.
     집안 성씨를 공유하는 것처럼 공통 뼈대를 이어받습니다.
  */
  final dog = Dog('초코');

  print('[레슨 1] 상속');
  dog.introduce();
  dog.bark();
  print('');
}

void lesson2Mixin() {
  final dog = Dog('나비');

  print('[레슨 2] 믹스인');
  print('  mixin 은 필요한 기능만 옆에서 붙이는 추가 도구 상자와 비슷합니다.');
  dog.jump();
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 06단계 : 상속과 믹스인');
  print('============================================================');
  print('');

  lesson1Inheritance();
  lesson2Mixin();
}
''',
    )

    write(
        "dart-learning/07_async_await/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 07단계: async와 await
===============================================================================
*/

Future<String> boilWater() async {
  await Future.delayed(const Duration(milliseconds: 300));
  return '물을 끓였습니다.';
}

Future<String> toastBread() async {
  await Future.delayed(const Duration(milliseconds: 100));
  return '빵을 구웠습니다.';
}

Future<void> lesson1Async() async {
  /*
     async 는 "끝날 때까지 오래 걸릴 수 있는 일"을 표시합니다.
     세탁기가 도는 동안 가만히 서 있기보다 다른 일을 하는 느낌과 비슷합니다.
  */
  print('[레슨 1] async');
  print('  오래 걸리는 작업을 Future 로 표현합니다.');
  print('');
}

Future<void> lesson2Await() async {
  print('[레슨 2] await');
  final water = await boilWater();
  final bread = await toastBread();
  print('  $water');
  print('  $bread');
  print('');
}

Future<void> main() async {
  print('============================================================');
  print('  Dart 07단계 : async와 await');
  print('============================================================');
  print('');

  await lesson1Async();
  await lesson2Await();
}
''',
    )

    write(
        "dart-learning/08_null_safety/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 08단계: null safety
===============================================================================
*/

void lesson1Nullable() {
  String? nickname;

  /*
     null safety 는 "비어 있을 수 있는 상자와 비어 있으면 안 되는 상자"를
     미리 구분하는 안전장치입니다.
     우유가 들어 있는 컵과 빈 컵을 구분하지 않으면 실수하기 쉽습니다.
  */
  print('[레슨 1] nullable 타입');
  print('  nickname 값: $nickname');
  print('');
}

void lesson2NullCheck() {
  String? nickname = '코딩왕';

  print('[레슨 2] null 체크');
  if (nickname != null) {
    print('  글자 수: ${nickname.length}');
  }
  print('');
}

void lesson3DefaultValue() {
  String? nickname;
  final safeName = nickname ?? '손님';

  print('[레슨 3] 기본값');
  print('  값이 없으면 $safeName 을 사용합니다.');
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 08단계 : null safety');
  print('============================================================');
  print('');

  lesson1Nullable();
  lesson2NullCheck();
  lesson3DefaultValue();
}
''',
    )

    write(
        "dart-learning/09_generics/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 09단계: 제네릭
===============================================================================
*/

class Box<T> {
  T? item;

  void put(T value) {
    item = value;
  }
}

void lesson1GenericBox() {
  /*
     제네릭은 "상자 모양은 같고, 내용물 타입만 바꾸는 기술"입니다.
     연필 상자, 공책 상자, 과자 상자를 따로 만들지 않고
     Box<T> 하나를 다양한 타입에 맞춰 재사용할 수 있습니다.
  */
  final stringBox = Box<String>()..put('연필');
  final intBox = Box<int>()..put(7);

  print('[레슨 1] 제네릭 상자');
  print('  문자열 상자: ${stringBox.item}');
  print('  숫자 상자  : ${intBox.item}');
  print('');
}

void lesson2WhyGeneric() {
  print('[레슨 2] 왜 좋을까?');
  print('  타입이 섞이는 실수를 줄이고, 같은 구조를 여러 번 재사용할 수 있습니다.');
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 09단계 : 제네릭');
  print('============================================================');
  print('');

  lesson1GenericBox();
  lesson2WhyGeneric();
}
''',
    )


if __name__ == "__main__":
    main()
