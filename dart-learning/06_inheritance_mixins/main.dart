/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 06단계: 상속과 믹스인
  ─ extends · super · override · abstract · implements · with · mixin ─

  ■ 실행: dart run main.dart
  ■ 컴파일: dart compile exe main.dart

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — 상속 기본 (extends)
// =====================================================================
/*
★ 상속 = "공통 기능을 부모 클래스에서 물려받기"

  비유: 집안 성씨
  - 부모 → 자식에게 성(name), 집 주소(address) 물려줌
  - 자식은 물려받은 것 + 자기만의 특기를 추가

  ┌────────────────────────────────────────────────┐
  │  Animal  (부모)                                │
  │  ├─ name, age                                  │
  │  ├─ eat()                                      │
  │  │                                             │
  │  ├── Dog  (자식)                               │
  │  │   ├─ bark()         ← 추가 기능             │
  │  │   └─ eat() override ← 부모 동작 바꾸기      │
  │  │                                             │
  │  └── Cat  (자식)                               │
  │      └─ meow()                                 │
  └────────────────────────────────────────────────┘

★ Dart 규칙
  - 단일 상속만 가능 (extends 는 하나만)
  - 다중 기능이 필요하면 mixin 사용 (레슨 4)
  - super 로 부모 생성자/메서드 호출
*/

class Animal {
  final String name;
  final int age;

  Animal(this.name, this.age);

  void eat() {
    print('  $name 이(가) 밥을 먹습니다.');
  }

  void introduce() {
    print('  저는 $name, ${age}살입니다.');
  }
}

class DogAnimal extends Animal {
  final String breed;   // 자식만의 추가 필드

  // super.name, super.age → 부모 생성자에 전달
  DogAnimal(super.name, super.age, this.breed);

  void bark() {
    print('  $name: 멍멍! (품종: $breed)');
  }

  // ── @override : 부모 메서드를 다시 정의 ──
  @override
  void eat() {
    super.eat();   // 부모의 eat() 도 호출 가능
    print('  $name 은(는) 사료를 먹습니다.');
  }
}

class CatAnimal extends Animal {
  CatAnimal(super.name, super.age);

  void meow() {
    print('  $name: 야옹~');
  }
}

void lesson1Inheritance() {
  print('[레슨 1] 상속 기본 (extends)');

  final dog = DogAnimal('초코', 3, '골든 리트리버');
  final cat = CatAnimal('나비', 2);

  dog.introduce();   // 부모에서 물려받은 메서드
  dog.bark();        // 자식만의 메서드
  dog.eat();         // 오버라이드된 메서드 (부모 + 자식 로직)

  cat.introduce();
  cat.meow();
  print('');
}


// =====================================================================
// 레슨 2 — abstract 클래스
// =====================================================================
/*
★ abstract 클래스 = "직접 인스턴스를 만들 수 없는 설계도"

  비유: 교과서의 목차
  - 목차(abstract)에는 "1장: 더하기" 라고 적혀 있지만 내용은 없음
  - 실제 교과서(concrete class)에서 내용을 채워야 함

  ┌──────────────────────────────────────────────┐
  │  abstract class Shape {                      │
  │    double area();     ← 본문 없음 (추상)     │
  │    double perimeter();                       │
  │  }                                           │
  │                                              │
  │  class Circle extends Shape {                │
  │    @override                                 │
  │    double area() => pi * r * r;  ← 구현      │
  │  }                                           │
  └──────────────────────────────────────────────┘

★ 왜 쓸까?
  - "이 메서드는 반드시 구현해야 한다" 라는 계약(contract) 역할
  - 빠뜨리면 컴파일 에러 → 안전!
*/

import 'dart:math' show pi;

abstract class Shape {
  // 추상 메서드 — 본문이 없음
  double area();
  double perimeter();

  // 일반 메서드 — 자식에서 그대로 사용 가능
  void printInfo() {
    print('  넓이: ${area().toStringAsFixed(2)}');
    print('  둘레: ${perimeter().toStringAsFixed(2)}');
  }
}

class Circle extends Shape {
  final double radius;
  Circle(this.radius);

  @override
  double area() => pi * radius * radius;

  @override
  double perimeter() => 2 * pi * radius;

  @override
  String toString() => 'Circle(반지름=$radius)';
}

class Rectangle extends Shape {
  final double width, height;
  Rectangle(this.width, this.height);

  @override
  double area() => width * height;

  @override
  double perimeter() => 2 * (width + height);

  @override
  String toString() => 'Rectangle(${width}x$height)';
}

void lesson2Abstract() {
  print('[레슨 2] abstract 클래스');

  // final shape = Shape();  ← 컴파일 에러! abstract 는 직접 생성 불가

  final shapes = <Shape>[
    Circle(5),
    Rectangle(4, 6),
    Circle(10),
  ];

  for (final s in shapes) {
    print('  $s');
    s.printInfo();
  }
  print('');
}


// =====================================================================
// 레슨 3 — implements (인터페이스)
// =====================================================================
/*
★ implements = "이 클래스의 모든 메서드를 내가 직접 구현하겠다"

  ┌────────────────────────────────────────────────────────┐
  │  extends     │ 부모 코드를 물려받음 (재사용 가능)      │
  │  implements  │ 모든 메서드를 처음부터 직접 구현         │
  │  with        │ mixin 기능을 끼워 넣음 (레슨 4)         │
  └────────────────────────────────────────────────────────┘

★ Dart 에는 interface 키워드가 없다!
  - 모든 클래스가 암묵적으로 인터페이스 역할 가능
  - implements 뒤에 클래스 이름을 쓰면 "그 클래스의 인터페이스를 구현"

★ 비유
  - extends = "아빠 회사를 물려받아 그대로 운영"
  - implements = "아빠 회사 이름만 따고 사업은 처음부터 내가 구성"
*/

class Printable {
  void printSelf() {
    print('  기본 출력');
  }
}

class Saveable {
  void save() {
    print('  기본 저장');
  }
}

// implements: Printable, Saveable 의 모든 메서드를 직접 구현해야 함
class Document implements Printable, Saveable {
  final String title;
  final String content;

  Document(this.title, this.content);

  @override
  void printSelf() {
    print('  📄 문서 출력: $title');
    print('  내용: $content');
  }

  @override
  void save() {
    print('  💾 문서 저장 완료: $title');
  }
}

void lesson3Implements() {
  print('[레슨 3] implements (인터페이스)');

  final doc = Document('보고서', '이번 달 성적 분석');
  doc.printSelf();
  doc.save();

  // 다형성: 부모 타입 변수에 자식 객체 담기
  final Printable p = doc;
  p.printSelf();    // Document 의 printSelf 실행
  print('');
}


// =====================================================================
// 레슨 4 — mixin (믹스인)
// =====================================================================
/*
★ mixin = "여러 클래스에 끼워 넣을 수 있는 기능 모듈"

  비유: 레고 블록
  - 클래스 = 기본 몸체
  - mixin  = 팔, 다리, 날개 같은 추가 블록
  - with 키워드로 끼워 넣기

  ┌──────────────────────────────────────────────────────┐
  │  mixin Fly {                                        │
  │    void fly() => print('날기!');                     │
  │  }                                                  │
  │                                                     │
  │  mixin Swim {                                       │
  │    void swim() => print('수영!');                    │
  │  }                                                  │
  │                                                     │
  │  class Duck extends Animal with Fly, Swim { }       │
  │                    ↑ 상속       ↑ mixin 끼워넣기     │
  └──────────────────────────────────────────────────────┘

★ mixin vs extends
  - extends: 하나만 가능 (단일 상속)
  - with:    여러 개 가능 (mixin 끼워 넣기)

★ mixin 제약
  - 생성자를 가질 수 없음 (Dart 3 에서 mixin class 도 가능)
  - on 키워드로 특정 클래스에만 사용 가능하게 제한
*/

mixin FlyMixin {
  void fly() {
    print('  ✈ 날개를 펼치고 하늘을 납니다!');
  }
}

mixin SwimMixin {
  void swim() {
    print('  🏊 물속에서 첨벙첨벙 수영합니다!');
  }
}

mixin SingMixin {
  void sing() {
    print('  🎵 노래를 부릅니다~ 짹짹');
  }
}

class Bird extends Animal with FlyMixin, SingMixin {
  Bird(super.name, super.age);
}

class Duck extends Animal with FlyMixin, SwimMixin {
  Duck(super.name, super.age);
}

class Fish extends Animal with SwimMixin {
  Fish(super.name, super.age);
}

void lesson4Mixin() {
  print('[레슨 4] mixin (믹스인)');

  final bird = Bird('참새', 1);
  bird.introduce();
  bird.fly();
  bird.sing();

  final duck = Duck('오리', 2);
  duck.introduce();
  duck.fly();
  duck.swim();

  final fish = Fish('금붕어', 1);
  fish.introduce();
  fish.swim();
  // fish.fly();  ← 컴파일 에러! Fish 에는 FlyMixin 이 없음
  print('');
}


// =====================================================================
// 레슨 5 — mixin on 제약과 mixin class
// =====================================================================
/*
★ on 키워드 = "이 mixin 은 특정 클래스에만 사용 가능"

  ┌──────────────────────────────────────────────────┐
  │  mixin Runner on Animal {                       │
  │    void run() {                                 │
  │      print('$name 이(가) 달립니다!');            │
  │      //     ↑ Animal 의 name 을 사용 가능       │
  │    }                                            │
  │  }                                              │
  │                                                 │
  │  class Horse extends Animal with Runner { }     │
  │  class Car with Runner { }  ← 에러! Car ≠ Animal│
  └──────────────────────────────────────────────────┘

★ mixin class (Dart 3.0+)
  - mixin 이면서 동시에 class 역할
  - 생성자를 가질 수 있고, extends 도 가능
*/

// on Animal: Animal 을 상속한 클래스에서만 사용 가능
mixin RunnerMixin on Animal {
  void run() {
    print('  🏃 $name 이(가) 전속력으로 달립니다!');
  }
}

class Horse extends Animal with RunnerMixin {
  Horse(super.name, super.age);
}

// ── mixin class 예시 (Dart 3) ──
mixin class Describable {
  String describe() => '설명 가능한 객체입니다.';
}

// mixin 으로도 쓸 수 있고, extends 로도 쓸 수 있음
class Product with Describable {
  final String name;
  Product(this.name);

  @override
  String describe() => '$name: 상품 설명';
}

void lesson5MixinAdvanced() {
  print('[레슨 5] mixin on 제약과 mixin class');

  final horse = Horse('번개', 5);
  horse.introduce();
  horse.run();

  final product = Product('다트 책');
  print('  ${product.describe()}');
  print('');
}


// =====================================================================
// 레슨 6 — 다형성 (Polymorphism)
// =====================================================================
/*
★ 다형성 = "같은 이름의 메서드가 객체에 따라 다르게 동작"

  비유: "소리 내기" 라는 같은 명령을 내려도
  - 강아지 → 멍멍
  - 고양이 → 야옹
  - 새     → 짹짹

  ┌──────────────────────────────────────────────────┐
  │  List<Animal> animals = [Dog(), Cat(), Bird()];  │
  │                                                  │
  │  for (final a in animals) {                      │
  │    a.eat();  ← 각 객체의 오버라이드된 eat() 실행 │
  │  }                                               │
  └──────────────────────────────────────────────────┘

★ is / as 키워드
  - is  : 타입 확인 (boolean)
  - as  : 타입 캐스팅 (실패 시 예외)
*/

void lesson6Polymorphism() {
  print('[레슨 6] 다형성');

  final animals = <Animal>[
    DogAnimal('초코', 3, '푸들'),
    CatAnimal('나비', 2),
    Bird('짹짹이', 1),
    Duck('도널드', 4),
  ];

  // 같은 Animal 타입이지만 각각 다른 행동
  for (final animal in animals) {
    animal.introduce();
    animal.eat();

    // is 로 타입 확인 후 전용 메서드 호출
    if (animal is DogAnimal) {
      animal.bark();
    } else if (animal is CatAnimal) {
      animal.meow();
    } else if (animal is Duck) {
      animal.swim();
    }
    print('  ---');
  }
  print('');
}


// =====================================================================
// 레슨 7 — 종합 정리: 상속 vs implements vs mixin
// =====================================================================
/*
★ 한눈에 비교

  ┌───────────┬──────────────────────┬──────────────────────┐
  │ 키워드    │ 의미                 │ 개수 제한            │
  ├───────────┼──────────────────────┼──────────────────────┤
  │ extends   │ 코드 물려받기        │ 1개만                │
  │ implements│ 인터페이스 구현      │ 여러 개 가능         │
  │ with      │ mixin 끼워 넣기      │ 여러 개 가능         │
  └───────────┴──────────────────────┴──────────────────────┘

★ 선택 가이드
  1. "부모의 코드를 그대로 재사용하고 싶다" → extends
  2. "이 메서드들을 반드시 구현하겠다"     → implements
  3. "여러 클래스에 공통 기능을 넣고 싶다"  → mixin + with
  4. 조합도 가능: class A extends B with C implements D { }
*/

abstract class Logger {
  void log(String message);
}

mixin TimestampMixin {
  String get timestamp {
    final now = DateTime.now();
    return '${now.hour}:${now.minute}:${now.second}';
  }
}

// extends Animal + with TimestampMixin + implements Logger
class SmartDog extends Animal with TimestampMixin implements Logger {
  SmartDog(super.name, super.age);

  @override
  void log(String message) {
    print('  [$timestamp] LOG: $message');
  }
}

void lesson7Summary() {
  print('[레슨 7] 종합 정리: extends vs implements vs mixin');

  final smartDog = SmartDog('똑똑이', 5);
  smartDog.introduce();       // extends Animal 의 메서드
  smartDog.log('밥 먹는 중'); // implements Logger 의 구현
  // timestamp 는 TimestampMixin 에서 온 것
  print('  현재 시각: ${smartDog.timestamp}');
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 06단계 : 상속과 믹스인');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1Inheritance();
  lesson2Abstract();
  lesson3Implements();
  lesson4Mixin();
  lesson5MixinAdvanced();
  lesson6Polymorphism();
  lesson7Summary();

  print('■■■ 06단계 완료! ■■■');
}
