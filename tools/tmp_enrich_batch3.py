# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def main():
    # C 후반부
    write(ROOT / "c-learning" / "15_networking" / "main.c", r'''
/*
===============================================================================
  C 학습 15단계: 네트워킹 기초
===============================================================================
*/

#include <stdio.h>

void lesson1_request_response(void);
void lesson2_ip_port(void);
void lesson3_protocols(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 15단계 : 네트워킹 기초\n");
    printf("============================================================\n\n");

    lesson1_request_response();
    lesson2_ip_port();
    lesson3_protocols();
    return 0;
}

void lesson1_request_response(void) {
    /*
      네트워크 통신은 "요청을 보내고 응답을 받는 흐름"이라고 생각하면 쉽습니다.
      식당에서 주문을 하고 음식이 오는 과정과 비슷합니다.
    */
    printf("[레슨 1] 요청과 응답\n");
    printf("  클라이언트 -> 서버 로 요청\n");
    printf("  서버 -> 클라이언트 로 응답\n\n");
}

void lesson2_ip_port(void) {
    /*
      IP = 건물 주소
      Port = 그 건물 안의 몇 번 방인지
      라고 생각하면 처음 이해가 쉽습니다.
    */
    printf("[레슨 2] IP 와 Port\n");
    printf("  IP   : 컴퓨터 주소\n");
    printf("  Port : 프로그램 출입문 번호\n\n");
}

void lesson3_protocols(void) {
    printf("[레슨 3] 프로토콜\n");
    printf("  HTTP  -> 웹에서 자주 쓰는 규칙\n");
    printf("  TCP   -> 순서를 지키며 보내는 규칙\n");
    printf("  UDP   -> 빠르지만 순서를 보장하지 않는 규칙\n\n");
}
''')

    write(ROOT / "c-learning" / "16_testing" / "main.c", r'''
/*
===============================================================================
  C 학습 16단계: 테스트 기초
===============================================================================
*/

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

void lesson1_what_is_test(void);
void lesson2_small_test(void);
void lesson3_why_needed(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 16단계 : 테스트 기초\n");
    printf("============================================================\n\n");

    lesson1_what_is_test();
    lesson2_small_test();
    lesson3_why_needed();
    return 0;
}

void lesson1_what_is_test(void) {
    printf("[레슨 1] 테스트란?\n");
    printf("  코드가 기대한 답을 내는지 자동으로 확인하는 과정입니다.\n\n");
}

void lesson2_small_test(void) {
    int result = add(2, 3);

    printf("[레슨 2] 아주 작은 테스트\n");
    printf("  예상값: 5\n");
    printf("  실제값: %d\n", result);
    printf("  통과 여부: %s\n\n", result == 5 ? "true" : "false");
}

void lesson3_why_needed(void) {
    printf("[레슨 3] 왜 테스트가 중요할까?\n");
    printf("  기능을 고친 뒤 예전 기능이 망가지지 않았는지 빨리 확인할 수 있습니다.\n\n");
}
''')

    write(ROOT / "c-learning" / "17_build_make" / "main.c", r'''
/*
===============================================================================
  C 학습 17단계: 빌드와 Make
===============================================================================
*/

#include <stdio.h>

void lesson1_compile_steps(void);
void lesson2_makefile_role(void);
void lesson3_common_commands(void);

int main(void) {
    printf("============================================================\n");
    printf("  C 17단계 : 빌드와 Make\n");
    printf("============================================================\n\n");

    lesson1_compile_steps();
    lesson2_makefile_role();
    lesson3_common_commands();
    return 0;
}

void lesson1_compile_steps(void) {
    /*
      C 프로그램은 보통
      소스코드 -> 컴파일 -> 실행파일
      흐름으로 만들어집니다.
    */
    printf("[레슨 1] 빌드 흐름\n");
    printf("  main.c -> 컴파일러 -> main.exe 또는 a.out\n\n");
}

void lesson2_makefile_role(void) {
    /*
      Makefile 은 "어떤 순서로 만들지 적어 둔 레시피"입니다.
    */
    printf("[레슨 2] Makefile 역할\n");
    printf("  바뀐 파일만 다시 빌드하도록 도와줍니다.\n\n");
}

void lesson3_common_commands(void) {
    printf("[레슨 3] 자주 보는 명령\n");
    printf("  gcc -Wall main.c -o app\n");
    printf("  make\n");
    printf("  make clean\n\n");
}
''')

    write(ROOT / "c-learning" / "18_real_project" / "main.c", r'''
/*
===============================================================================
  C 학습 18단계: 실전 미니 프로젝트 - 학생 점수 관리기
===============================================================================
*/

#include <stdio.h>

typedef struct {
    char name[20];
    int score;
} Student;

void print_students(Student students[], int size);
double find_average(Student students[], int size);

int main(void) {
    Student students[3] = {
        {"민수", 82},
        {"지우", 95},
        {"서연", 68}
    };

    printf("============================================================\n");
    printf("  C 18단계 : 실전 미니 프로젝트\n");
    printf("============================================================\n\n");

    print_students(students, 3);
    printf("[평균 점수]\n");
    printf("  %.2f\n", find_average(students, 3));
    return 0;
}

void print_students(Student students[], int size) {
    printf("[학생 목록]\n");
    for (int i = 0; i < size; i++) {
        const char* result = students[i].score >= 70 ? "통과" : "복습 필요";
        printf("  %s: %d점 -> %s\n", students[i].name, students[i].score, result);
    }
    printf("\n");
}

double find_average(Student students[], int size) {
    int total = 0;
    for (int i = 0; i < size; i++) {
        total += students[i].score;
    }
    return (double)total / size;
}
''')

    # C# 중반~후반
    write(ROOT / "csharp-learning" / "06_inheritance_polymorphism" / "Program.cs", r'''
/*
===============================================================================
  C# 학습 06단계: 상속과 다형성
===============================================================================
*/

using System;
using System.Text;

namespace Lesson06
{
    class Animal
    {
        public virtual void Speak()
        {
            Console.WriteLine("동물이 소리를 냅니다.");
        }
    }

    class Dog : Animal
    {
        public override void Speak()
        {
            Console.WriteLine("강아지가 멍멍 짖습니다.");
        }
    }

    class Cat : Animal
    {
        public override void Speak()
        {
            Console.WriteLine("고양이가 야옹 웁니다.");
        }
    }

    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 06단계 : 상속과 다형성");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Console.WriteLine("[레슨 1] 상속");
            Console.WriteLine("  부모 클래스의 공통 기능을 자식 클래스가 물려받습니다.");
            Console.WriteLine();

            Console.WriteLine("[레슨 2] 다형성");
            Animal[] animals = { new Dog(), new Cat() };
            foreach (var animal in animals)
            {
                animal.Speak();
            }
        }
    }
}
''')

    write(ROOT / "csharp-learning" / "07_interfaces_generics" / "Program.cs", r'''
/*
===============================================================================
  C# 학습 07단계: 인터페이스와 제네릭
===============================================================================
*/

using System;
using System.Text;

namespace Lesson07
{
    interface IPrinter
    {
        void Print();
    }

    class Student : IPrinter
    {
        public string Name { get; set; } = "";

        public void Print()
        {
            Console.WriteLine("학생 이름: " + Name);
        }
    }

    class Box<T>
    {
        public T Value { get; }

        public Box(T value)
        {
            Value = value;
        }
    }

    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 07단계 : 인터페이스와 제네릭");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Console.WriteLine("[레슨 1] 인터페이스");
            var student = new Student { Name = "민수" };
            student.Print();
            Console.WriteLine();

            Console.WriteLine("[레슨 2] 제네릭");
            var intBox = new Box<int>(10);
            var stringBox = new Box<string>("안녕하세요");
            Console.WriteLine("  intBox  = " + intBox.Value);
            Console.WriteLine("  stringBox = " + stringBox.Value);
        }
    }
}
''')

    write(ROOT / "csharp-learning" / "17_build_deploy" / "Program.cs", r'''
/*
===============================================================================
  C# 학습 17단계: 빌드와 배포
===============================================================================
*/

using System;
using System.Text;

namespace Lesson17
{
    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 17단계 : 빌드와 배포");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Console.WriteLine("[레슨 1] 빌드");
            Console.WriteLine("  dotnet build 는 실행 파일을 만들기 위한 준비 과정입니다.");
            Console.WriteLine();

            Console.WriteLine("[레슨 2] 배포");
            Console.WriteLine("  dotnet publish 는 실제 배포용 결과물을 모아 줍니다.");
            Console.WriteLine();

            Console.WriteLine("[레슨 3] 체크리스트");
            Console.WriteLine("  1. 설정 파일 확인");
            Console.WriteLine("  2. 환경 변수 확인");
            Console.WriteLine("  3. 테스트 확인");
        }
    }
}
''')

    write(ROOT / "csharp-learning" / "18_real_project" / "Program.cs", r'''
/*
===============================================================================
  C# 학습 18단계: 실전 미니 프로젝트
===============================================================================
*/

using System;
using System.Collections.Generic;
using System.Text;

namespace Lesson18
{
    class Student
    {
        public string Name { get; set; } = "";
        public int Score { get; set; }
    }

    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            var students = new List<Student>
            {
                new Student { Name = "민수", Score = 82 },
                new Student { Name = "지우", Score = 95 },
                new Student { Name = "서연", Score = 68 },
            };

            Console.WriteLine("============================================================");
            Console.WriteLine("  C# 18단계 : 실전 미니 프로젝트");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            Console.WriteLine("[학생 목록]");
            foreach (var student in students)
            {
                string result = student.Score >= 70 ? "통과" : "복습 필요";
                Console.WriteLine($"  {student.Name}: {student.Score}점 -> {result}");
            }
        }
    }
}
''')

    # Go 남은 부분 일부
    write(ROOT / "go-learning" / "15_cli_tools" / "main.go", r'''
/*
===============================================================================
  Go 학습 15단계: CLI 도구 만들기
===============================================================================
*/

package main

import "fmt"

func lesson1WhatIsCLI() {
    fmt.Println("[레슨 1] CLI 란?")
    fmt.Println("  마우스 대신 명령어로 움직이는 도구입니다.")
    fmt.Println()
}

func lesson2ArgumentIdea() {
    fmt.Println("[레슨 2] 인자(argument)")
    fmt.Println("  프로그램 뒤에 붙이는 추가 정보입니다.")
    fmt.Println("  예: app.exe hello")
    fmt.Println()
}

func lesson3MiniCommand() {
    fmt.Println("[레슨 3] 미니 명령 예시")
    fmt.Println("  hello -> 인사하기")
    fmt.Println("  add 2 3 -> 더하기")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 15단계 : CLI 도구 만들기")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1WhatIsCLI()
    lesson2ArgumentIdea()
    lesson3MiniCommand()
}
''')

    write(ROOT / "go-learning" / "17_build_deploy" / "main.go", r'''
/*
===============================================================================
  Go 학습 17단계: 빌드와 배포
===============================================================================
*/

package main

import "fmt"

func lesson1Build() {
    fmt.Println("[레슨 1] 빌드")
    fmt.Println("  go build 는 실행 파일을 만들어 줍니다.")
    fmt.Println()
}

func lesson2CrossCompile() {
    fmt.Println("[레슨 2] 크로스 컴파일")
    fmt.Println("  다른 운영체제용 실행 파일도 만들 수 있습니다.")
    fmt.Println("  예: GOOS=windows GOARCH=amd64 go build")
    fmt.Println()
}

func lesson3Deploy() {
    fmt.Println("[레슨 3] 배포")
    fmt.Println("  만들어진 실행 파일을 서버나 사용자 컴퓨터로 옮깁니다.")
    fmt.Println()
}

func main() {
    fmt.Println("============================================================")
    fmt.Println("  Go 17단계 : 빌드와 배포")
    fmt.Println("============================================================")
    fmt.Println()

    lesson1Build()
    lesson2CrossCompile()
    lesson3Deploy()
}
''')

    write(ROOT / "go-learning" / "18_real_project" / "main.go", r'''
/*
===============================================================================
  Go 학습 18단계: 실전 미니 프로젝트
===============================================================================
*/

package main

import "fmt"

type Student struct {
    Name  string
    Score int
}

func printStudents(students []Student) {
    fmt.Println("[학생 목록]")
    for _, student := range students {
        result := "복습 필요"
        if student.Score >= 70 {
            result = "통과"
        }
        fmt.Printf("  %s: %d점 -> %s\n", student.Name, student.Score, result)
    }
    fmt.Println()
}

func main() {
    students := []Student{
        {"민수", 82},
        {"지우", 95},
        {"서연", 68},
    }

    fmt.Println("============================================================")
    fmt.Println("  Go 18단계 : 실전 미니 프로젝트")
    fmt.Println("============================================================")
    fmt.Println()

    printStudents(students)
}
''')

    # Rust 일부
    write(ROOT / "rust-learning" / "15_async_await" / "src/main.rs", r'''
// =============================================================================
//   Rust 학습 15단계: async와 await
// =============================================================================

fn lesson1_concept() {
    println!("[레슨 1] async/await 이란?");
    println!("  기다리는 시간을 덜 낭비하게 도와주는 비동기 문법입니다.");
    println!();
}

fn lesson2_analogy() {
    println!("[레슨 2] 비유");
    println!("  물이 끓는 동안 그릇을 준비하는 것과 비슷합니다.");
    println!();
}

fn lesson3_note() {
    println!("[레슨 3] 주의");
    println!("  async 함수만 있다고 바로 돌아가는 것은 아니고 실행기(runtime)도 필요합니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 15단계 : async와 await");
    println!("============================================================");
    println!();

    lesson1_concept();
    lesson2_analogy();
    lesson3_note();
}
''')

    write(ROOT / "rust-learning" / "16_testing" / "src/main.rs", r'''
// =============================================================================
//   Rust 학습 16단계: 테스트
// =============================================================================

fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn lesson1_concept() {
    println!("[레슨 1] 테스트란?");
    println!("  코드가 기대한 값을 내는지 자동으로 확인하는 과정입니다.");
    println!();
}

fn lesson2_small_check() {
    let result = add(2, 3);
    println!("[레슨 2] 작은 확인");
    println!("  예상값: 5");
    println!("  실제값: {}", result);
    println!("  통과 여부: {}", result == 5);
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 16단계 : 테스트");
    println!("============================================================");
    println!();

    lesson1_concept();
    lesson2_small_check();
}
''')

    write(ROOT / "rust-learning" / "17_build_deploy" / "src/main.rs", r'''
// =============================================================================
//   Rust 학습 17단계: 빌드와 배포
// =============================================================================

fn lesson1_build() {
    println!("[레슨 1] 빌드");
    println!("  cargo build 는 개발용 빌드");
    println!("  cargo build --release 는 배포용 최적화 빌드");
    println!();
}

fn lesson2_deploy() {
    println!("[레슨 2] 배포");
    println!("  release 폴더 안 결과물을 서버나 사용자 환경으로 옮깁니다.");
    println!();
}

fn main() {
    println!("============================================================");
    println!("  Rust 17단계 : 빌드와 배포");
    println!("============================================================");
    println!();

    lesson1_build();
    lesson2_deploy();
}
''')

    write(ROOT / "rust-learning" / "18_real_project" / "src/main.rs", r'''
// =============================================================================
//   Rust 학습 18단계: 실전 미니 프로젝트
// =============================================================================

struct Student {
    name: String,
    score: i32,
}

fn print_students(students: &[Student]) {
    println!("[학생 목록]");
    for student in students {
        let result = if student.score >= 70 { "통과" } else { "복습 필요" };
        println!("  {}: {}점 -> {}", student.name, student.score, result);
    }
    println!();
}

fn main() {
    let students = vec![
        Student { name: String::from("민수"), score: 82 },
        Student { name: String::from("지우"), score: 95 },
        Student { name: String::from("서연"), score: 68 },
    ];

    println!("============================================================");
    println!("  Rust 18단계 : 실전 미니 프로젝트");
    println!("============================================================");
    println!();

    print_students(&students);
}
''')


if __name__ == "__main__":
    main()
