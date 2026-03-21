# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(path: str, content: str) -> None:
    file_path = ROOT / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content.strip() + "\n", encoding="utf-8")


def main() -> None:
    write(
        "c-learning/10_advanced_pointers/main.c",
        r'''
/*
===============================================================================
  C 학습 10단계: 고급 포인터
===============================================================================
*/

#include <stdio.h>

void lesson1_pointer_to_pointer(void);
void lesson2_array_and_pointer(void);
void lesson3_function_with_pointer(void);
void lesson4_common_mistakes(void);

void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main(void) {
    printf("============================================================\n");
    printf("  C 10단계 : 고급 포인터\n");
    printf("============================================================\n\n");

    lesson1_pointer_to_pointer();
    lesson2_array_and_pointer();
    lesson3_function_with_pointer();
    lesson4_common_mistakes();
    return 0;
}

void lesson1_pointer_to_pointer(void) {
    int score = 90;
    int* ptr = &score;
    int** ptr2 = &ptr;

    /*
      포인터는 주소를 가리키는 화살표입니다.
      이중 포인터는 "화살표를 가리키는 또 다른 화살표"입니다.
      처음엔 낯설지만, 주소를 한 단계 더 추적하는 구조라고 보면 됩니다.
    */
    printf("[레슨 1] 이중 포인터\n");
    printf("  score 값           = %d\n", score);
    printf("  *ptr               = %d\n", *ptr);
    printf("  **ptr2             = %d\n\n", **ptr2);
}

void lesson2_array_and_pointer(void) {
    int values[3] = {10, 20, 30};
    int* p = values;

    printf("[레슨 2] 배열과 포인터\n");
    printf("  values[0] = %d\n", values[0]);
    printf("  *(p + 1)  = %d\n", *(p + 1));
    printf("  배열 이름은 시작 주소처럼 쓰일 수 있습니다.\n\n");
}

void lesson3_function_with_pointer(void) {
    int a = 3;
    int b = 7;

    printf("[레슨 3] 포인터로 값 바꾸기\n");
    printf("  바꾸기 전: a=%d, b=%d\n", a, b);
    swap(&a, &b);
    printf("  바꾼 후  : a=%d, b=%d\n\n", a, b);
}

void lesson4_common_mistakes(void) {
    printf("[레슨 4] 자주 하는 실수\n");
    printf("  1. 초기화하지 않은 포인터를 바로 사용합니다.\n");
    printf("  2. * 와 & 의 역할을 뒤섞습니다.\n");
    printf("  3. 배열 범위를 넘어서 포인터 이동을 합니다.\n\n");
}
''',
    )

    write(
        "c-learning/11_debugging/main.c",
        r'''
/*
===============================================================================
  C 학습 11단계: 디버깅
===============================================================================
*/

#include <stdio.h>

int average(int values[], int count) {
    int total = 0;
    for (int i = 0; i < count; i++) {
        total += values[i];
    }
    return total / count;
}

void lesson1_trace_values(void);
void lesson2_find_danger(void);
void lesson3_debug_habit(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 11단계 : 디버깅\n");
    printf("============================================================\n\n");

    lesson1_trace_values();
    lesson2_find_danger();
    lesson3_debug_habit();
    return 0;
}

void lesson1_trace_values(void) {
    int scores[3] = {80, 90, 70};

    printf("[레슨 1] 값 추적\n");
    printf("  scores[0] = %d\n", scores[0]);
    printf("  scores[1] = %d\n", scores[1]);
    printf("  scores[2] = %d\n", scores[2]);
    printf("  average   = %d\n\n", average(scores, 3));
}

void lesson2_find_danger(void) {
    /*
      디버깅은 감으로 맞히는 게임이 아닙니다.
      값이 어디서 들어오고, 어디서 바뀌고, 어디서 깨지는지
      한 줄씩 추적하는 과정입니다.
    */
    printf("[레슨 2] 위험 지점 찾기\n");
    printf("  count 가 0 이면 total / count 에서 0으로 나누게 됩니다.\n");
    printf("  즉, 함수 인자 검사가 중요합니다.\n\n");
}

void lesson3_debug_habit(void) {
    printf("[레슨 3] 디버깅 습관\n");
    printf("  1. 입력값을 먼저 출력해 봅니다.\n");
    printf("  2. 중간 계산값을 단계별로 확인합니다.\n");
    printf("  3. 정상 케이스 말고 실패 케이스도 직접 만듭니다.\n\n");
}
''',
    )

    write(
        "c-learning/12_data_structures/main.c",
        r'''
/*
===============================================================================
  C 학습 12단계: 자료구조
===============================================================================
*/

#include <stdio.h>

typedef struct {
    int data[5];
    int top;
} Stack;

void push(Stack* stack, int value) {
    if (stack->top < 4) {
        stack->top++;
        stack->data[stack->top] = value;
    }
}

int pop(Stack* stack) {
    if (stack->top >= 0) {
        int value = stack->data[stack->top];
        stack->top--;
        return value;
    }
    return -1;
}

void lesson1_why_data_structure(void);
void lesson2_stack_example(void);
void lesson3_analogy(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 12단계 : 자료구조\n");
    printf("============================================================\n\n");

    lesson1_why_data_structure();
    lesson2_stack_example();
    lesson3_analogy();
    return 0;
}

void lesson1_why_data_structure(void) {
    /*
      자료구조는 "데이터를 어떤 모양의 상자에 담을지 정하는 기술"입니다.
      같은 장난감도 서랍, 바구니, 책장에 따라 꺼내는 속도가 달라지듯
      데이터도 구조에 따라 처리 방식이 달라집니다.
    */
    printf("[레슨 1] 자료구조란?\n");
    printf("  정리 방식이 달라지면 꺼내고 넣는 속도도 달라집니다.\n\n");
}

void lesson2_stack_example(void) {
    Stack stack = {{0, 0, 0, 0, 0}, -1};

    push(&stack, 10);
    push(&stack, 20);
    push(&stack, 30);

    printf("[레슨 2] 스택 예제\n");
    printf("  마지막에 넣은 값이 먼저 나옵니다.\n");
    printf("  pop -> %d\n", pop(&stack));
    printf("  pop -> %d\n\n", pop(&stack));
}

void lesson3_analogy(void) {
    printf("[레슨 3] 비유\n");
    printf("  스택은 접시 더미와 비슷합니다.\n");
    printf("  맨 위 접시를 먼저 꺼내기 쉽기 때문에 LIFO 구조라고 부릅니다.\n\n");
}
''',
    )

    write(
        "c-learning/13_algorithms/main.c",
        r'''
/*
===============================================================================
  C 학습 13단계: 알고리즘
===============================================================================
*/

#include <stdio.h>

void bubble_sort(int values[], int count) {
    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - 1 - i; j++) {
            if (values[j] > values[j + 1]) {
                int temp = values[j];
                values[j] = values[j + 1];
                values[j + 1] = temp;
            }
        }
    }
}

void lesson1_algorithm_mindset(void);
void lesson2_sort_example(void);
void lesson3_step_by_step(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 13단계 : 알고리즘\n");
    printf("============================================================\n\n");

    lesson1_algorithm_mindset();
    lesson2_sort_example();
    lesson3_step_by_step();
    return 0;
}

void lesson1_algorithm_mindset(void) {
    /*
      알고리즘은 "문제를 푸는 순서표"입니다.
      라면을 끓일 때도 물 올리기 -> 면 넣기 -> 스프 넣기 순서가 있듯,
      프로그램도 문제를 푸는 절차가 필요합니다.
    */
    printf("[레슨 1] 알고리즘이란?\n");
    printf("  문제를 푸는 방법을 순서로 적은 것입니다.\n\n");
}

void lesson2_sort_example(void) {
    int values[5] = {30, 10, 50, 20, 40};

    bubble_sort(values, 5);

    printf("[레슨 2] 버블 정렬\n");
    for (int i = 0; i < 5; i++) {
        printf("  values[%d] = %d\n", i, values[i]);
    }
    printf("\n");
}

void lesson3_step_by_step(void) {
    printf("[레슨 3] 왜 버블 정렬이 될까?\n");
    printf("  옆 친구 둘을 비교해서 큰 값을 뒤로 보내는 일을 반복합니다.\n");
    printf("  그래서 한 바퀴가 끝날 때마다 가장 큰 값이 맨 뒤로 이동합니다.\n\n");
}
''',
    )

    write(
        "c-learning/14_bit_operations/main.c",
        r'''
/*
===============================================================================
  C 학습 14단계: 비트 연산
===============================================================================
*/

#include <stdio.h>

void lesson1_binary_view(void);
void lesson2_and_or_xor(void);
void lesson3_shift(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 14단계 : 비트 연산\n");
    printf("============================================================\n\n");

    lesson1_binary_view();
    lesson2_and_or_xor();
    lesson3_shift();
    return 0;
}

void lesson1_binary_view(void) {
    /*
      컴퓨터는 결국 0과 1로 값을 저장합니다.
      비트 연산은 전등 스위치를 켜고 끄듯,
      아주 작은 단위의 켜짐/꺼짐을 직접 다루는 작업입니다.
    */
    printf("[레슨 1] 2진수 관점\n");
    printf("  5는 2진수로 0101, 3은 0011 처럼 볼 수 있습니다.\n\n");
}

void lesson2_and_or_xor(void) {
    int a = 5;
    int b = 3;

    printf("[레슨 2] AND / OR / XOR\n");
    printf("  a & b = %d\n", a & b);
    printf("  a | b = %d\n", a | b);
    printf("  a ^ b = %d\n\n", a ^ b);
}

void lesson3_shift(void) {
    int value = 4;

    printf("[레슨 3] 시프트 연산\n");
    printf("  value << 1 = %d\n", value << 1);
    printf("  value >> 1 = %d\n", value >> 1);
    printf("  왼쪽 시프트는 자릿수를 왼쪽으로 밀어 2배 효과처럼 보일 수 있습니다.\n\n");
}
''',
    )

    write(
        "rust-learning/10_modern_rust/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 10단계: 모던 Rust
// =============================================================================

#[derive(Debug)]
struct Student {
    name: String,
    score: i32,
}

fn lesson1_if_let() {
    let nickname = Some("코딩왕");

    /*
       if let 은 "이 상자 안에 값이 있으면 그 값만 꺼내서 쓰자"는 문법입니다.
       모든 경우를 길게 match 하지 않아도 되는 짧은 문입니다.
    */
    println!("[레슨 1] if let");
    if let Some(name) = nickname {
        println!("  별명: {}", name);
    }
    println!();
}

fn lesson2_iterator_chain() {
    let scores = vec![55, 72, 88, 91, 64];
    let passed: Vec<i32> = scores.into_iter().filter(|score| *score >= 70).collect();

    println!("[레슨 2] 체이닝 문법");
    println!("  통과 점수: {:?}", passed);
    println!();
}

fn lesson3_struct_update() {
    let original = Student {
        name: String::from("민수"),
        score: 80,
    };

    let updated = Student {
        score: 95,
        ..original
    };

    println!("[레슨 3] 구조체 업데이트");
    println!("  변경된 학생 정보: {:?}", updated);
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 10단계 : 모던 Rust");
    println!("============================================================");
    println!();

    lesson1_if_let();
    lesson2_iterator_chain();
    lesson3_struct_update();
}
''',
    )

    write(
        "rust-learning/11_debugging/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 11단계: 디버깅
// =============================================================================

fn average(values: &[i32]) -> i32 {
    let total: i32 = values.iter().sum();
    total / values.len() as i32
}

fn lesson1_trace() {
    let scores = vec![80, 90, 70];

    println!("[레슨 1] 값 추적");
    println!("  입력값: {:?}", scores);
    println!("  평균  : {}", average(&scores));
    println!();
}

fn lesson2_find_problem() {
    /*
       디버깅은 에러 메시지를 읽는 것에서 끝나지 않습니다.
       어떤 입력에서, 어떤 줄에서, 어떤 값 때문에 문제가 생겼는지
       흐름을 재현하는 것이 핵심입니다.
    */
    println!("[레슨 2] 문제 지점");
    println!("  빈 벡터가 들어오면 values.len() 이 0 이라서 나누기에서 위험합니다.");
    println!("  즉, 정상 입력뿐 아니라 빈 입력도 함께 테스트해야 합니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 11단계 : 디버깅");
    println!("============================================================");
    println!();

    lesson1_trace();
    lesson2_find_problem();
}
''',
    )

    write(
        "rust-learning/12_cargo_crates/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 12단계: Cargo와 크레이트
// =============================================================================

fn lesson1_cargo() {
    /*
       Cargo 는 Rust 프로젝트의 매니저입니다.
       요리사가 재료 목록, 조리 순서, 완성 확인을 한 번에 관리하듯
       Cargo 도 빌드, 실행, 테스트, 의존성 관리를 같이 담당합니다.
    */
    println!("[레슨 1] Cargo");
    println!("  cargo build : 빌드");
    println!("  cargo run   : 실행");
    println!("  cargo test  : 테스트");
    println!();
}

fn lesson2_crate() {
    println!("[레슨 2] crate");
    println!("  crate 는 Rust 코드 묶음입니다.");
    println!("  작은 장난감 상자 하나가 crate 라면, 여러 상자를 모은 방이 프로젝트라고 볼 수 있습니다.");
    println!();
}

fn lesson3_dependency() {
    println!("[레슨 3] 의존성");
    println!("  Cargo.toml 에 필요한 외부 crate 이름과 버전을 적습니다.");
    println!("  그러면 Cargo 가 부품을 자동으로 가져와 연결해 줍니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 12단계 : Cargo와 크레이트");
    println!("============================================================");
    println!();

    lesson1_cargo();
    lesson2_crate();
    lesson3_dependency();
}
''',
    )

    write(
        "rust-learning/13_generics_lifetimes/src/main.rs",
        r'''
// =============================================================================
//   Rust 학습 13단계: 제네릭과 라이프타임
// =============================================================================

fn largest<T: PartialOrd + Copy>(a: T, b: T) -> T {
    if a > b { a } else { b }
}

fn lesson1_generics() {
    /*
       제네릭은 "틀은 하나인데 내용물 타입은 바꿀 수 있는" 방식입니다.
       같은 비교 함수를 숫자용, 실수용으로 따로 만들지 않고
       공통 규칙만 있으면 한 번에 재사용할 수 있습니다.
    */
    println!("[레슨 1] 제네릭");
    println!("  큰 값 찾기: {}", largest(10, 20));
    println!("  큰 값 찾기: {}", largest(3.5, 2.1));
    println!();
}

fn lesson2_lifetime_idea() {
    println!("[레슨 2] 라이프타임 아이디어");
    println!("  라이프타임은 '이 참조가 얼마나 오래 안전하게 살아 있는가'를 알려 주는 표지판입니다.");
    println!("  빌린 책을 반납했는데 계속 읽으려 하면 안 되듯, 참조도 원본보다 오래 살 수 없습니다.");
    println!();
}

fn lesson3_why_rust_is_strict() {
    println!("[레슨 3] 왜 이렇게 엄격할까?");
    println!("  나중에 터질 메모리 버그를 컴파일 단계에서 먼저 막기 위해서입니다.");
    println!("  처음엔 까다롭지만, 큰 프로젝트로 갈수록 안전 장치의 가치가 커집니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 13단계 : 제네릭과 라이프타임");
    println!("============================================================");
    println!();

    lesson1_generics();
    lesson2_lifetime_idea();
    lesson3_why_rust_is_strict();
}
''',
    )

    write(
        "dart-learning/10_file_io/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 10단계: 파일 입출력
===============================================================================
*/

import 'dart:io';

Future<void> lesson1WriteFile() async {
  /*
     파일은 공책처럼 데이터를 남겨 두는 저장 공간입니다.
     메모리 안의 값은 프로그램이 꺼지면 사라질 수 있지만,
     파일에 적어 두면 나중에 다시 읽을 수 있습니다.
  */
  final file = File('dart-learning/10_file_io/sample.txt');
  await file.writeAsString('사과\n바나나\n포도\n');

  print('[레슨 1] 파일 쓰기');
  print('  sample.txt 에 과일 목록을 저장했습니다.');
  print('');
}

Future<void> lesson2ReadFile() async {
  final file = File('dart-learning/10_file_io/sample.txt');
  final lines = await file.readAsLines();

  print('[레슨 2] 파일 읽기');
  for (final line in lines) {
    print('  읽은 줄: $line');
  }
  print('');
}

void lesson3WhyAsync() {
  print('[레슨 3] 왜 async 로 읽을까?');
  print('  파일 읽기는 시간이 걸릴 수 있어서 앱이 멈춘 것처럼 보이지 않게 비동기로 처리합니다.');
  print('  큰 상자를 옮길 때 다른 사람을 기다리게 하지 않는 것과 비슷합니다.');
  print('');
}

Future<void> main() async {
  print('============================================================');
  print('  Dart 10단계 : 파일 입출력');
  print('============================================================');
  print('');

  await lesson1WriteFile();
  await lesson2ReadFile();
  lesson3WhyAsync();
}
''',
    )

    write(
        "dart-learning/11_debugging/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 11단계: 디버깅
===============================================================================
*/

int average(List<int> scores) {
  final total = scores.reduce((a, b) => a + b);
  return total ~/ scores.length;
}

void lesson1Trace() {
  final scores = [80, 90, 70];

  print('[레슨 1] 값 추적');
  print('  입력값: $scores');
  print('  평균  : ${average(scores)}');
  print('');
}

void lesson2DangerCase() {
  /*
     디버깅은 "왜 안 되지?"를 중얼거리는 시간이 아니라,
     입력값과 중간값을 확인하며 문제를 좁혀 가는 과정입니다.
     빈 리스트가 들어오면 reduce 와 나누기에서 문제가 생길 수 있습니다.
  */
  print('[레슨 2] 위험 사례');
  print('  빈 리스트는 average 함수에서 실패할 수 있습니다.');
  print('  그래서 경계값 테스트가 중요합니다.');
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 11단계 : 디버깅');
  print('============================================================');
  print('');

  lesson1Trace();
  lesson2DangerCase();
}
''',
    )

    write(
        "dart-learning/12_packages/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 12단계: 패키지
===============================================================================
*/

void lesson1PackageIdea() {
  /*
     패키지는 재사용 가능한 도구 상자입니다.
     날짜 계산, HTTP 통신, 상태 관리 같은 기능을
     내가 모두 처음부터 만들지 않게 도와줍니다.
  */
  print('[레슨 1] 패키지란?');
  print('  pubspec.yaml 에 필요한 패키지 이름과 버전을 적어 관리합니다.');
  print('');
}

void lesson2WhyUseful() {
  print('[레슨 2] 왜 유용할까?');
  print('  이미 검증된 기능을 가져와 개발 속도를 높일 수 있습니다.');
  print('  다만 너무 많이 가져오면 프로젝트가 무거워질 수 있습니다.');
  print('');
}

void lesson3Analogy() {
  print('[레슨 3] 비유');
  print('  집을 지을 때 망치, 드라이버, 전동공구를 직접 만들지 않는 것과 같습니다.');
  print('  필요한 도구를 골라서 가져오는 것이 패키지 사용입니다.');
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 12단계 : 패키지');
  print('============================================================');
  print('');

  lesson1PackageIdea();
  lesson2WhyUseful();
  lesson3Analogy();
}
''',
    )

    write(
        "dart-learning/13_design_patterns/main.dart",
        r'''
/*
===============================================================================
  Dart 학습 13단계: 디자인 패턴
===============================================================================
*/

abstract class DiscountStrategy {
  int apply(int price);
}

class NoDiscount implements DiscountStrategy {
  @override
  int apply(int price) => price;
}

class StudentDiscount implements DiscountStrategy {
  @override
  int apply(int price) => price - 1000;
}

void printPrice(DiscountStrategy strategy, int price) {
  print('  원래 가격: $price');
  print('  할인 결과: ${strategy.apply(price)}');
}

void lesson1PatternMindset() {
  /*
     패턴은 외울 단어집이 아니라, 자주 풀어 본 문제의 좋은 해답 모음입니다.
     어떤 구조를 왜 쓰는지 연결해서 이해해야 실제 프로젝트에 적용할 수 있습니다.
  */
  print('[레슨 1] 패턴 관점');
  print('  중요한 것은 이름보다 문제와 해결 방식의 연결입니다.');
  print('');
}

void lesson2Strategy() {
  print('[레슨 2] Strategy 예제');
  printPrice(NoDiscount(), 5000);
  printPrice(StudentDiscount(), 5000);
  print('');
}

void lesson3Analogy() {
  print('[레슨 3] 비유');
  print('  같은 상품도 일반 가격, 학생 가격처럼 계산 규칙이 달라질 수 있습니다.');
  print('  이 규칙을 바꿔 끼우는 방식이 Strategy 패턴입니다.');
  print('');
}

void main() {
  print('============================================================');
  print('  Dart 13단계 : 디자인 패턴');
  print('============================================================');
  print('');

  lesson1PatternMindset();
  lesson2Strategy();
  lesson3Analogy();
}
''',
    )

    write(
        "go-learning/16_design_patterns/main.go",
        r'''
/*
===============================================================================
  Go 학습 16단계: 디자인 패턴
===============================================================================
*/

package main

import "fmt"

type DiscountStrategy interface {
    Apply(price int) int
}

type NoDiscount struct{}
type StudentDiscount struct{}

func (NoDiscount) Apply(price int) int      { return price }
func (StudentDiscount) Apply(price int) int { return price - 1000 }

func printPrice(strategy DiscountStrategy, price int) {
    fmt.Println("  원래 가격:", price)
    fmt.Println("  할인 결과:", strategy.Apply(price))
}

func lesson1PatternMindset() {
    /*
       패턴은 멋있어 보이는 모양 모음이 아닙니다.
       비슷한 설계 문제를 만났을 때 덜 흔들리게 해 주는 경험 정리입니다.
       그래서 이름만 외우기보다 "왜 이 구조가 필요한가"를 먼저 봐야 합니다.
    */
    fmt.Println("[레슨 1] 패턴 관점")
    fmt.Println("  자주 만나는 문제를 검증된 방식으로 풀기 위한 생각 틀입니다.")
    fmt.Println()
}

func lesson2Strategy() {
    fmt.Println("[레슨 2] Strategy 예제")
    printPrice(NoDiscount{}, 5000)
    printPrice(StudentDiscount{}, 5000)
    fmt.Println()
}

func lesson3Analogy() {
    fmt.Println("[레슨 3] 비유")
    fmt.Println("  같은 물건이라도 손님 종류에 따라 가격 계산 규칙이 달라질 수 있습니다.")
    fmt.Println("  계산 방식을 바꿔 끼우는 것이 Strategy 패턴의 핵심입니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 16단계 : 디자인 패턴")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1PatternMindset()
    lesson2Strategy()
    lesson3Analogy()
}
''',
    )


if __name__ == "__main__":
    main()
