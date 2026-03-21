/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Rust 학습 07단계: 컬렉션 (Collections)
  ─ Vec, String, HashMap, HashSet, BTreeMap, 이터레이터 ─

  [학습 목표]
  1. Vec<T> 의 생성, 수정, 접근, 소유권 규칙을 안다
  2. String 과 &str 의 차이를 이해한다
  3. HashMap 으로 키-값 쌍을 관리한다
  4. HashSet 으로 중복 없는 집합을 만든다
  5. 컬렉션과 소유권의 관계를 파악한다
  6. 이터레이터로 컬렉션을 효율적으로 처리한다

  ■ 실행: cargo run
  ■ 빌드: cargo build --release

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

use std::collections::{HashMap, HashSet, BTreeMap};

// =====================================================================
// 레슨 1 — Vec<T>: 가변 길이 배열
// =====================================================================
/*
★ Vec<T> 는 Rust 에서 가장 많이 쓰는 컬렉션
  → 힙에 저장, 크기가 늘어나거나 줄어들 수 있음
  → C++ 의 std::vector 와 비슷

  비유: 늘어나는 서랍장
  ┌────┬────┬────┬────┬ ··· ┐
  │ 70 │ 80 │ 90 │100 │     │  ← 필요하면 서랍 추가
  └────┴────┴────┴────┴ ··· ┘

★ 내부 구조 (3개의 값으로 구성)
  ┌──────────────────────────────────────┐
  │ ptr  → 힙 데이터의 시작 주소         │
  │ len  → 현재 들어있는 원소 수         │
  │ cap  → 재할당 없이 담을 수 있는 용량 │
  └──────────────────────────────────────┘

★ 소유권: Vec 은 안에 담긴 데이터를 소유합니다
  → Vec 이 drop 되면 안의 모든 원소도 drop!
*/

fn lesson1_vec_basics() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 1: Vec<T> 기본");
    println!("═══════════════════════════════════════════");

    // ── 생성 방법들 ──
    let v1: Vec<i32> = Vec::new();           // 빈 벡터
    let v2 = vec![10, 20, 30];              // 매크로로 초기화
    let v3 = vec![0; 5];                     // [0, 0, 0, 0, 0]
    println!("  v1(빈): {:?}", v1);
    println!("  v2: {:?}", v2);
    println!("  v3: {:?}", v3);

    // ── 추가와 삭제 ──
    let mut scores = vec![70, 80, 90];
    scores.push(100);                        // 끝에 추가
    scores.insert(0, 60);                    // 인덱스 0에 삽입
    println!("  push/insert 후: {:?}", scores);

    let removed = scores.pop();              // 마지막 원소 꺼내기
    println!("  pop: {:?}, 남은: {:?}", removed, scores);

    scores.remove(0);                        // 인덱스 0 삭제
    println!("  remove(0) 후: {:?}", scores);

    // ── 안전한 접근 vs 위험한 접근 ──
    // 인덱스 접근: 범위 밖이면 panic!
    println!("  scores[0] = {}", scores[0]);

    // .get() 접근: Option 반환 → 안전!
    match scores.get(100) {
        Some(val) => println!("  scores[100] = {}", val),
        None      => println!("  scores[100] → 범위 밖! (안전하게 처리)"),
    }

    // ── 길이와 용량 ──
    println!("  길이: {}, 용량: {}", scores.len(), scores.capacity());

    // ── 정렬, 뒤집기, 중복제거 ──
    let mut nums = vec![3, 1, 4, 1, 5, 9, 2, 6, 5];
    nums.sort();
    println!("  정렬: {:?}", nums);
    nums.dedup();    // 연속된 중복만 제거 (정렬 후 사용!)
    println!("  중복제거: {:?}", nums);
    nums.reverse();
    println!("  뒤집기: {:?}", nums);
    println!();
}

// =====================================================================
// 레슨 2 — Vec 과 소유권: 빌림 규칙 주의!
// =====================================================================
/*
★ Vec 에서 원소를 빌리면, Vec 자체를 수정할 수 없다!

  비유: 도서관에서 책을 빌려준 동안 서가를 이동하면
        빌린 사람이 찾아올 주소가 바뀌어 버림!

  ┌───────────────────────────────────────────────────────┐
  │ let mut v = vec![1, 2, 3];                           │
  │ let first = &v[0];   // 불변 참조 빌림                │
  │ v.push(4);           // ← 컴파일 에러!               │
  │                      // push 가 재할당할 수 있어서    │
  │                      // first 가 무효가 될 수 있음    │
  │ println!("{}", first);                                │
  └───────────────────────────────────────────────────────┘
*/

fn lesson2_vec_ownership() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 2: Vec 과 소유권");
    println!("═══════════════════════════════════════════");

    // ── 이동 (move) ──
    let v1 = vec![String::from("안녕"), String::from("세계")];
    let v2 = v1;       // v1 의 소유권이 v2 로 이동
    // println!("{:?}", v1);  // ← 컴파일 에러!
    println!("  v2 (이동된 벡터): {:?}", v2);

    // ── iter vs into_iter ──
    // iter()    → &T 참조로 순회 (원본 유지)
    // into_iter → T 값으로 순회 (원본 소비)
    let names = vec!["철수", "영희", "민수"];
    for name in names.iter() {
        print!("  {}  ", name);
    }
    println!();
    println!("  names 아직 사용 가능: {:?}", names);

    let owned = vec![String::from("A"), String::from("B")];
    for item in owned.into_iter() {
        print!("  소비: {}  ", item);
    }
    println!();
    // println!("{:?}", owned);  // ← 컴파일 에러! into_iter 로 소비됨

    // ── 슬라이스(&[T]) 로 빌려주기 ──
    let data = vec![10, 20, 30, 40, 50];
    let slice = &data[1..4];   // [20, 30, 40]
    println!("  슬라이스: {:?}", slice);
    println!();
}

// =====================================================================
// 레슨 3 — String 과 &str: 문자열의 두 얼굴
// =====================================================================
/*
★ Rust 문자열은 항상 유효한 UTF-8 입니다!

  ┌──────────────┬─────────────────────────────────────────┐
  │ String       │ 소유하는 문자열 (힙, 크기 가변)         │
  │              │ → Vec<u8> 의 래퍼                       │
  │ &str         │ 빌린 문자열 조각 (문자열 슬라이스)      │
  │              │ → 수정 불가, 가벼움                     │
  └──────────────┴─────────────────────────────────────────┘

  비유:
  ┌────────────────────────────────────────────────┐
  │ String = 내가 소유한 노트 (추가/삭제 자유)     │
  │ &str   = 교과서 한 페이지 사진 (읽기만 가능)   │
  └────────────────────────────────────────────────┘

★ 한글은 글자당 3바이트!
  → "가".len() == 3 (바이트)
  → "가".chars().count() == 1 (글자 수)
  → 인덱싱 s[0] 불가! (바이트 경계 문제)
*/

fn lesson3_string() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 3: String 과 &str");
    println!("═══════════════════════════════════════════");

    // ── 생성 ──
    let s1 = String::from("안녕하세요");
    let s2 = "Rust".to_string();
    let s3: &str = "리터럴은 &str";

    println!("  s1: {}", s1);
    println!("  s2: {}", s2);
    println!("  s3: {}", s3);

    // ── 결합 ──
    let mut greeting = String::from("Hello");
    greeting.push(' ');             // char 추가
    greeting.push_str("World");     // &str 추가
    println!("  결합: {}", greeting);

    // format! 매크로 (소유권 이동 없음!)
    let full = format!("{} {}", s1, s2);
    println!("  format!: {}", full);
    println!("  s1 아직 사용 가능: {}", s1);  // format! 은 참조만 사용

    // ── UTF-8 주의사항 ──
    let korean = "가나다";
    println!("  '가나다' 바이트 수: {}", korean.len());         // 9
    println!("  '가나다' 글자 수: {}", korean.chars().count()); // 3
    // println!("{}", &korean[0..1]);  // ← panic! 바이트 경계 아님

    // 안전하게 글자 단위 접근
    for (i, ch) in korean.chars().enumerate() {
        println!("    [{}] = '{}'", i, ch);
    }

    // ── 유용한 메서드들 ──
    let text = "  Hello, Rust!  ";
    println!("  trim: '{}'", text.trim());
    println!("  contains: {}", text.contains("Rust"));
    println!("  replace: {}", text.replace("Rust", "World"));

    let csv = "철수,영희,민수";
    let names: Vec<&str> = csv.split(',').collect();
    println!("  split: {:?}", names);
    println!();
}

// =====================================================================
// 레슨 4 — HashMap<K, V>: 이름표로 값 찾기
// =====================================================================
/*
★ HashMap = 키(이름표)로 값을 빠르게 찾는 사전
  → Python 의 dict, Java 의 HashMap 과 같은 역할

  비유: 사물함
  ┌──────────┬─────────┐
  │ "철수"   │ 92점    │
  │ "영희"   │ 88점    │
  │ "민수"   │ 75점    │
  └──────────┴─────────┘
  → 이름으로 바로 점수를 찾을 수 있다!

★ 소유권 주의:
  - String 을 키로 넣으면 HashMap 이 소유권을 가져감
  - &str 을 키로 쓰면 라이프타임 필요
  - i32 같은 Copy 타입은 복사됨
*/

fn lesson4_hashmap() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 4: HashMap<K, V>");
    println!("═══════════════════════════════════════════");

    // ── 생성과 삽입 ──
    let mut scores: HashMap<String, i32> = HashMap::new();
    scores.insert(String::from("철수"), 92);
    scores.insert(String::from("영희"), 88);
    scores.insert(String::from("민수"), 75);

    // ── 조회 ──
    // get() 은 Option<&V> 반환!
    if let Some(score) = scores.get("철수") {
        println!("  철수 점수: {}", score);
    }
    println!("  서연 점수: {:?}", scores.get("서연"));  // None

    // ── 덮어쓰기 ──
    scores.insert(String::from("민수"), 80);  // 기존 값 덮어씀
    println!("  민수 변경 후: {:?}", scores.get("민수"));

    // ── 없을 때만 삽입: entry API ──
    scores.entry(String::from("서연")).or_insert(95);  // 없으니 삽입
    scores.entry(String::from("철수")).or_insert(0);    // 이미 있으니 무시
    println!("  서연 (새로 삽입): {:?}", scores.get("서연"));
    println!("  철수 (변경 안 됨): {:?}", scores.get("철수"));

    // ── 순회 ──
    println!("  전체 목록:");
    for (name, score) in &scores {
        println!("    {} → {}점", name, score);
    }

    // ── entry 로 값 갱신 (단어 빈도수 세기) ──
    let text = "사과 바나나 사과 포도 바나나 사과";
    let mut word_count: HashMap<&str, i32> = HashMap::new();
    for word in text.split_whitespace() {
        let count = word_count.entry(word).or_insert(0);
        *count += 1;   // 가변 참조를 통해 값 증가
    }
    println!("  단어 빈도: {:?}", word_count);
    println!();
}

// =====================================================================
// 레슨 5 — HashSet<T>: 중복 없는 집합
// =====================================================================
/*
★ HashSet = 값만 있고 키가 없는 HashMap
  → 중복을 자동으로 제거
  → 집합 연산 (합집합, 교집합, 차집합) 지원

  ┌─────────────────────────────────────┐
  │ HashSet  → 순서 보장 없음, 빠름     │
  │ BTreeSet → 정렬된 순서 유지         │
  └─────────────────────────────────────┘
*/

fn lesson5_hashset() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 5: HashSet<T>");
    println!("═══════════════════════════════════════════");

    let mut fruits: HashSet<&str> = HashSet::new();
    fruits.insert("사과");
    fruits.insert("바나나");
    fruits.insert("포도");
    fruits.insert("사과");  // 중복 → 무시됨!

    println!("  과일 집합: {:?}", fruits);
    println!("  개수: {} (사과 중복 제거됨)", fruits.len());
    println!("  사과 포함? {}", fruits.contains("사과"));

    // ── 집합 연산 ──
    let set_a: HashSet<i32> = [1, 2, 3, 4, 5].iter().cloned().collect();
    let set_b: HashSet<i32> = [3, 4, 5, 6, 7].iter().cloned().collect();

    let union: HashSet<&i32> = set_a.union(&set_b).collect();
    let intersection: HashSet<&i32> = set_a.intersection(&set_b).collect();
    let difference: HashSet<&i32> = set_a.difference(&set_b).collect();

    println!("  A: {:?}", set_a);
    println!("  B: {:?}", set_b);
    println!("  합집합: {:?}", union);
    println!("  교집합: {:?}", intersection);
    println!("  차집합(A-B): {:?}", difference);
    println!();
}

// =====================================================================
// 레슨 6 — BTreeMap: 정렬된 맵
// =====================================================================
/*
★ HashMap vs BTreeMap

  ┌──────────────┬──────────────────────────────────────┐
  │ HashMap      │ 해시 기반, 빠름 (O(1)), 순서 없음    │
  │ BTreeMap     │ 트리 기반, O(log n), 키 순서 보장     │
  └──────────────┴──────────────────────────────────────┘

  → 정렬된 순서로 출력하고 싶으면 BTreeMap!
  → 범위 조회(range)가 필요하면 BTreeMap!
*/

fn lesson6_btreemap() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 6: BTreeMap (정렬된 맵)");
    println!("═══════════════════════════════════════════");

    let mut rankings: BTreeMap<i32, &str> = BTreeMap::new();
    rankings.insert(3, "민수");
    rankings.insert(1, "서연");
    rankings.insert(2, "철수");

    // 키 순서대로 출력됨!
    println!("  순위표 (자동 정렬):");
    for (rank, name) in &rankings {
        println!("    {}등: {}", rank, name);
    }

    // ── 범위 조회 ──
    let mut monthly_sales: BTreeMap<u32, i32> = BTreeMap::new();
    for month in 1..=12 {
        monthly_sales.insert(month, (month as i32) * 1000 + 500);
    }

    println!("  1분기 매출 (범위 조회):");
    for (month, sales) in monthly_sales.range(1..=3) {
        println!("    {}월: {}원", month, sales);
    }
    println!();
}

// =====================================================================
// 레슨 7 — 이터레이터로 컬렉션 처리하기
// =====================================================================
/*
★ 이터레이터 = 컬렉션을 한 원소씩 처리하는 컨베이어 벨트

  ┌──────────────────────────────────────────────────────┐
  │ .iter()      → &T  (불변 참조, 원본 유지)            │
  │ .iter_mut()  → &mut T (가변 참조, 원본 수정)         │
  │ .into_iter() → T   (소유권 이동, 원본 소비)          │
  └──────────────────────────────────────────────────────┘

★ 자주 쓰는 어댑터
  ┌───────────────┬──────────────────────────────────────┐
  │ map()         │ 각 원소를 변환                       │
  │ filter()      │ 조건에 맞는 것만 남김                │
  │ enumerate()   │ (인덱스, 값) 쌍으로 변환             │
  │ zip()         │ 두 이터레이터를 짝지어 합침          │
  │ take(n)       │ 앞에서 n 개만                        │
  │ skip(n)       │ 앞에서 n 개 건너뛰기                 │
  │ flatten()     │ 중첩 구조를 평탄화                   │
  │ chain()       │ 두 이터레이터를 이어붙임             │
  └───────────────┴──────────────────────────────────────┘

★ 소비자 (최종 연산)
  ┌───────────────┬──────────────────────────────────────┐
  │ collect()     │ 컬렉션으로 모으기                    │
  │ sum()         │ 합계                                 │
  │ count()       │ 개수                                 │
  │ min() / max() │ 최솟값 / 최댓값                      │
  │ any() / all() │ 하나라도 / 전부 조건 만족?           │
  │ find()        │ 조건에 맞는 첫 번째 원소             │
  │ fold()        │ 누적 연산                            │
  └───────────────┴──────────────────────────────────────┘
*/

fn lesson7_iterators() {
    println!("═══════════════════════════════════════════");
    println!(" 레슨 7: 이터레이터 활용");
    println!("═══════════════════════════════════════════");

    let scores = vec![55, 72, 88, 91, 64, 78, 95];

    // ── filter + map + collect ──
    let passed: Vec<String> = scores.iter()
        .filter(|&&s| s >= 70)
        .map(|s| format!("{}점(통과)", s))
        .collect();
    println!("  통과자: {:?}", passed);

    // ── sum, min, max ──
    let total: i32 = scores.iter().sum();
    let avg = total as f64 / scores.len() as f64;
    println!("  합계: {}, 평균: {:.1}", total, avg);
    println!("  최고: {:?}, 최저: {:?}", scores.iter().max(), scores.iter().min());

    // ── enumerate ──
    println!("  인덱스와 함께:");
    for (i, score) in scores.iter().enumerate() {
        print!("  [{}]={} ", i, score);
    }
    println!();

    // ── zip: 두 컬렉션 짝짓기 ──
    let names = vec!["철수", "영희", "민수"];
    let grades = vec!["A", "B", "C"];
    let roster: Vec<(&str, &str)> = names.iter()
        .copied()
        .zip(grades.iter().copied())
        .collect();
    println!("  zip 결과: {:?}", roster);

    // ── fold: 누적 연산 ──
    let product = vec![2, 3, 4].iter().fold(1, |acc, &x| acc * x);
    println!("  2*3*4 = {}", product);

    // ── any / all ──
    let has_perfect = scores.iter().any(|&s| s == 100);
    let all_passed = scores.iter().all(|&s| s >= 60);
    println!("  100점 있나? {} | 전원 60점 이상? {}", has_perfect, all_passed);
    println!();
}

// =====================================================================
//  main
// =====================================================================

fn main() {
    println!();
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  Rust 07단계: 컬렉션 (Collections)");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!();

    lesson1_vec_basics();
    lesson2_vec_ownership();
    lesson3_string();
    lesson4_hashmap();
    lesson5_hashset();
    lesson6_btreemap();
    lesson7_iterators();

    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
    println!("  07단계 완료! 다음은 08_error_handling 입니다");
    println!("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■");
}
