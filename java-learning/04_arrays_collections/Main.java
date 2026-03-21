/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Java 학습 04단계: 배열과 컬렉션
  ─ Arrays, ArrayList, LinkedList, HashMap, HashSet ─

  ■ 컴파일: javac Main.java
  ■ 실행:   java Main

  배열과 컬렉션은 여러 개의 데이터를 한꺼번에 다루는 도구예요!
  마치 여러 물건을 담는 "바구니"나 "서랍장"처럼요!

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Arrays;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Main {

    public static void main(String[] args) {

        // ═══════════════════════════════════════════════════
        //  섹션 1: 1차원 배열 (1D Array)
        // ═══════════════════════════════════════════════════

        /*
         * 배열(Array)이란?
         *
         * 같은 종류의 값을 여러 개 담는 "고정된 칸막이 서랍"이에요.
         *
         * 마치 학교 사물함처럼요:
         * - 1번 사물함 = [0번 인덱스]
         * - 2번 사물함 = [1번 인덱스]  ← 인덱스는 0부터 시작해요!
         * - ...
         *
         * 배열의 특징:
         * 1. 크기가 고정돼요 (한번 만들면 늘리거나 줄일 수 없어요!)
         * 2. 같은 타입의 값만 넣을 수 있어요
         * 3. 인덱스(번호)로 빠르게 찾을 수 있어요
         */

        System.out.println("=== 1차원 배열 ===");

        // 배열 선언 방법 1: 처음부터 값을 넣기
        int[] scores = {85, 92, 78, 95, 88};
        // 배열 선언 방법 2: 크기만 먼저 정하기
        int[] emptyArr = new int[5];  // 5칸짜리 빈 배열 (기본값 0으로 채워짐)
        String[] names = new String[3]; // 기본값 null로 채워짐

        // 값 넣기
        names[0] = "철수";
        names[1] = "영희";
        names[2] = "민준";

        // 배열 출력
        System.out.println("이름 배열:");
        for (int i = 0; i < names.length; i++) {
            System.out.println("  names[" + i + "] = " + names[i]);
        }

        System.out.println("\n점수 배열:");
        for (int score : scores) {
            System.out.print(score + " ");
        }
        System.out.println();

        // 배열의 길이 = .length
        System.out.println("배열 길이: " + scores.length + "개");

        // 배열 합계, 평균
        int total = 0;
        for (int score : scores) {
            total += score;
        }
        System.out.println("총점: " + total + "점");
        System.out.printf("평균: %.1f점%n", (double)total / scores.length);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 2: 2차원 배열 (2D Array)
        // ═══════════════════════════════════════════════════

        /*
         * 2차원 배열이란?
         *
         * 배열 안에 배열이 들어있는 것이에요!
         * 마치 교실의 자리 배치처럼요.
         * (줄 번호, 열 번호)로 자리를 찾아요!
         *
         * 예: 3줄 4열 교실
         * [0][0] [0][1] [0][2] [0][3]   ← 1줄
         * [1][0] [1][1] [1][2] [1][3]   ← 2줄
         * [2][0] [2][1] [2][2] [2][3]   ← 3줄
         */

        System.out.println("=== 2차원 배열 ===");

        // 3행 3열 배열 (구구단 일부)
        int[][] multiTable = {
            {1, 2, 3},   // 1행
            {2, 4, 6},   // 2행
            {3, 6, 9}    // 3행
        };

        System.out.println("곱셈표:");
        for (int i = 0; i < multiTable.length; i++) {
            for (int j = 0; j < multiTable[i].length; j++) {
                System.out.printf("%3d", multiTable[i][j]);
            }
            System.out.println();
        }

        // 성적표 (학생 × 과목)
        String[] students = {"철수", "영희", "민준"};
        String[] subjects = {"국어", "수학", "영어"};
        int[][] grades = {
            {90, 85, 88},  // 철수의 국어, 수학, 영어
            {78, 92, 80},  // 영희의 국어, 수학, 영어
            {95, 70, 93}   // 민준의 국어, 수학, 영어
        };

        System.out.println("\n성적표:");
        System.out.printf("%-6s", "이름");
        for (String subject : subjects) {
            System.out.printf("%6s", subject);
        }
        System.out.println();
        System.out.println("─".repeat(25));

        for (int i = 0; i < students.length; i++) {
            System.out.printf("%-6s", students[i]);
            for (int j = 0; j < subjects.length; j++) {
                System.out.printf("%6d", grades[i][j]);
            }
            System.out.println();
        }

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 3: Arrays 유틸리티 클래스
        // ═══════════════════════════════════════════════════

        /*
         * Arrays 클래스란?
         *
         * 배열을 쉽게 다룰 수 있는 도구 모음이에요!
         * 마치 도구 상자에서 필요한 도구를 꺼내 쓰는 것처럼요.
         *
         * Arrays.sort()    → 정렬 (작은 것부터 큰 것 순서로)
         * Arrays.toString() → 배열을 문자열로 예쁘게 출력
         * Arrays.fill()    → 배열을 특정 값으로 채우기
         * Arrays.copyOf()  → 배열 복사
         * Arrays.binarySearch() → 값 찾기 (정렬된 배열에서)
         */

        System.out.println("=== Arrays 유틸리티 ===");

        int[] numbers = {5, 3, 8, 1, 9, 2, 7, 4, 6};
        System.out.println("원본: " + Arrays.toString(numbers));

        // 정렬 (오름차순)
        Arrays.sort(numbers);
        System.out.println("정렬 후: " + Arrays.toString(numbers));

        // 배열 채우기
        int[] filled = new int[5];
        Arrays.fill(filled, 7);
        System.out.println("7로 채우기: " + Arrays.toString(filled));

        // 배열 복사
        int[] original = {1, 2, 3, 4, 5};
        int[] copied = Arrays.copyOf(original, 3);       // 처음 3개만
        int[] copied2 = Arrays.copyOfRange(original, 1, 4); // 1~3번 인덱스
        System.out.println("원본: " + Arrays.toString(original));
        System.out.println("처음 3개 복사: " + Arrays.toString(copied));
        System.out.println("1~3번 복사: " + Arrays.toString(copied2));

        // 이진 탐색 (정렬된 배열에서 값 찾기)
        int[] sortedArr = {1, 3, 5, 7, 9, 11, 13};
        int index = Arrays.binarySearch(sortedArr, 7);
        System.out.println("7의 위치: " + index + "번째");

        // 배열 비교
        int[] arr1 = {1, 2, 3};
        int[] arr2 = {1, 2, 3};
        int[] arr3 = {1, 2, 4};
        System.out.println("arr1 == arr2 (주소비교): " + (arr1 == arr2));  // false
        System.out.println("Arrays.equals(arr1, arr2): " + Arrays.equals(arr1, arr2)); // true
        System.out.println("Arrays.equals(arr1, arr3): " + Arrays.equals(arr1, arr3)); // false

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 4: ArrayList<E>
        // ═══════════════════════════════════════════════════

        /*
         * ArrayList란?
         *
         * 배열보다 편리한 목록이에요!
         * 배열은 크기가 고정이지만, ArrayList는
         * 자유롭게 늘리거나 줄일 수 있어요!
         *
         * 마치 배열은 "정해진 칸의 사물함",
         * ArrayList는 "필요할 때마다 칸을 늘릴 수 있는 마법 사물함"이에요!
         *
         * <E>는 제네릭(Generic)이에요.
         * "어떤 타입을 담을지 미리 알려줘요"
         * ArrayList<String> → String만 담는 리스트
         * ArrayList<Integer> → 정수만 담는 리스트
         */

        System.out.println("=== ArrayList ===");

        // ArrayList 생성
        ArrayList<String> fruits = new ArrayList<>();
        // 아직 비어있어요 (size = 0)

        // add() - 끝에 추가
        fruits.add("사과");
        fruits.add("바나나");
        fruits.add("포도");
        fruits.add("수박");
        fruits.add("딸기");
        System.out.println("과일 목록: " + fruits);
        System.out.println("크기: " + fruits.size() + "개");

        // add(인덱스, 값) - 특정 위치에 삽입
        fruits.add(2, "망고");  // 2번 위치에 망고 삽입
        System.out.println("망고 추가 후: " + fruits);

        // get() - 특정 위치 값 가져오기
        System.out.println("0번째: " + fruits.get(0));
        System.out.println("2번째: " + fruits.get(2));

        // set() - 특정 위치 값 변경
        fruits.set(0, "풋사과");
        System.out.println("사과→풋사과: " + fruits);

        // remove() - 삭제
        fruits.remove("수박");         // 값으로 삭제
        fruits.remove(0);              // 인덱스로 삭제
        System.out.println("수박, 0번째 삭제: " + fruits);

        // contains() - 포함 여부 확인
        System.out.println("바나나 있나요? " + fruits.contains("바나나"));
        System.out.println("수박 있나요? " + fruits.contains("수박"));

        // indexOf() - 위치 찾기
        System.out.println("바나나 위치: " + fruits.indexOf("바나나") + "번째");

        // isEmpty() - 비어있는지 확인
        System.out.println("비어있나요? " + fruits.isEmpty());

        // 반복
        System.out.println("남은 과일:");
        for (String fruit : fruits) {
            System.out.println("  - " + fruit);
        }

        // clear() - 전체 삭제
        fruits.clear();
        System.out.println("전체 삭제 후 크기: " + fruits.size());

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 5: LinkedList<E>
        // ═══════════════════════════════════════════════════

        /*
         * LinkedList란?
         *
         * 각 항목이 이전/다음 항목을 서로 연결(link)하는 구조예요!
         *
         * ArrayList vs LinkedList:
         * - ArrayList: 각 항목에 번호로 바로 접근 (빠름)
         *              중간 삽입/삭제는 느림 (나머지를 다 옮겨야 함)
         *
         * - LinkedList: 각 항목이 체인처럼 연결됨
         *               중간 삽입/삭제가 빠름 (연결만 바꾸면 됨)
         *               특정 항목 접근은 느림 (처음부터 세어야 함)
         *
         * 마치:
         * ArrayList = 번호 있는 사물함 (번호로 바로 찾기)
         * LinkedList = 손 잡고 서있는 줄 (줄 중간에 새 친구 끼워넣기 쉬움)
         */

        System.out.println("=== LinkedList ===");

        LinkedList<String> queue = new LinkedList<>();

        // 뒤에 추가
        queue.add("첫 번째");
        queue.add("두 번째");
        queue.add("세 번째");
        System.out.println("LinkedList: " + queue);

        // 앞에 추가 (addFirst)
        queue.addFirst("맨 앞");
        System.out.println("맨 앞 추가: " + queue);

        // 뒤에 추가 (addLast)
        queue.addLast("맨 뒤");
        System.out.println("맨 뒤 추가: " + queue);

        // 앞에서 꺼내기 (Queue처럼 사용)
        String first = queue.pollFirst();  // 꺼내면 목록에서 사라져요!
        System.out.println("앞에서 꺼낸 값: " + first);
        System.out.println("꺼낸 후: " + queue);

        // 뒤에서 꺼내기 (Stack처럼 사용)
        String last = queue.pollLast();
        System.out.println("뒤에서 꺼낸 값: " + last);
        System.out.println("꺼낸 후: " + queue);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 6: HashMap<K, V>
        // ═══════════════════════════════════════════════════

        /*
         * HashMap이란?
         *
         * "키(Key)"와 "값(Value)"을 쌍으로 저장하는 구조예요!
         * 마치 사전처럼요!
         * "사과" → "apple"
         * "바나나" → "banana"
         *
         * 키로 값을 찾아요 (마치 이름으로 전화번호 찾기!)
         *
         * K = Key의 타입
         * V = Value의 타입
         *
         * 특징:
         * - 키는 중복 불가! (같은 키로 넣으면 덮어씌워요)
         * - 값은 중복 가능
         * - 순서가 없어요 (넣은 순서대로 나오지 않을 수 있어요)
         */

        System.out.println("=== HashMap ===");

        // 전화번호부 만들기
        HashMap<String, String> phoneBook = new HashMap<>();

        // put() - 키-값 쌍 추가
        phoneBook.put("철수", "010-1234-5678");
        phoneBook.put("영희", "010-9876-5432");
        phoneBook.put("민준", "010-1111-2222");
        phoneBook.put("소연", "010-3333-4444");

        System.out.println("전화번호부: " + phoneBook);

        // get() - 키로 값 찾기
        System.out.println("철수 번호: " + phoneBook.get("철수"));
        System.out.println("없는 사람: " + phoneBook.get("없는사람")); // null 반환

        // getOrDefault() - 없으면 기본값 반환
        System.out.println("없는 사람(기본값): " + phoneBook.getOrDefault("없는사람", "번호 없음"));

        // containsKey() - 키 존재 여부
        System.out.println("철수 있나요? " + phoneBook.containsKey("철수"));

        // put()으로 수정
        phoneBook.put("철수", "010-9999-0000");  // 같은 키면 값이 바뀌어요
        System.out.println("철수 번호 변경: " + phoneBook.get("철수"));

        // remove() - 삭제
        phoneBook.remove("소연");
        System.out.println("소연 삭제 후: " + phoneBook);

        // size() - 개수
        System.out.println("연락처 수: " + phoneBook.size() + "명");

        // 모든 키-값 쌍 출력
        System.out.println("전화번호부 전체:");
        for (Map.Entry<String, String> entry : phoneBook.entrySet()) {
            System.out.println("  " + entry.getKey() + " : " + entry.getValue());
        }

        // 키만 출력
        System.out.print("이름 목록: ");
        for (String name : phoneBook.keySet()) {
            System.out.print(name + " ");
        }
        System.out.println();

        // 값만 출력
        System.out.print("번호 목록: ");
        for (String phone : phoneBook.values()) {
            System.out.print(phone + " ");
        }
        System.out.println();

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 7: HashSet<E>
        // ═══════════════════════════════════════════════════

        /*
         * HashSet이란?
         *
         * 중복 없이 값을 저장하는 구조예요!
         * 마치 반 학생 명단처럼 같은 이름이 두 번 나올 수 없어요.
         *
         * 특징:
         * - 중복 불가! (같은 값을 넣어도 한 개만 저장)
         * - 순서 없음 (넣은 순서와 다르게 나올 수 있어요)
         * - 빠른 검색 (있는지 없는지 확인이 빠름)
         *
         * 언제 쓰나요?
         * - 중복 제거할 때
         * - 특정 값이 목록에 있는지 빠르게 확인할 때
         */

        System.out.println("=== HashSet ===");

        HashSet<String> uniqueFruits = new HashSet<>();
        uniqueFruits.add("사과");
        uniqueFruits.add("바나나");
        uniqueFruits.add("사과");   // 중복! 저장 안 돼요
        uniqueFruits.add("포도");
        uniqueFruits.add("바나나"); // 중복! 저장 안 돼요
        uniqueFruits.add("딸기");

        System.out.println("유니크 과일 목록: " + uniqueFruits);
        System.out.println("크기: " + uniqueFruits.size() + "개 (중복 제거됨!)");

        // 포함 여부 확인
        System.out.println("사과 있나요? " + uniqueFruits.contains("사과"));
        System.out.println("망고 있나요? " + uniqueFruits.contains("망고"));

        // ArrayList의 중복 제거에 활용!
        System.out.println("\nArrayList 중복 제거 예제:");
        ArrayList<Integer> withDuplicates = new ArrayList<>();
        withDuplicates.add(1); withDuplicates.add(2); withDuplicates.add(3);
        withDuplicates.add(2); withDuplicates.add(1); withDuplicates.add(4);
        System.out.println("중복 있는 목록: " + withDuplicates);

        HashSet<Integer> noDuplicates = new HashSet<>(withDuplicates);
        System.out.println("중복 제거 후: " + noDuplicates);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 8: Iterator (반복자)
        // ═══════════════════════════════════════════════════

        /*
         * Iterator(반복자)란?
         *
         * 컬렉션의 항목을 하나씩 꺼내보는 도구예요!
         * 마치 선물 상자에서 선물을 하나씩 꺼내보는 것처럼요.
         *
         * hasNext() → 다음 항목이 있나요? (true/false)
         * next()    → 다음 항목을 가져와요
         * remove()  → 현재 항목을 삭제해요
         *
         * 반복 중에 삭제할 때 특히 유용해요!
         * (for-each로 반복하면서 삭제하면 오류가 나요!)
         */

        System.out.println("=== Iterator ===");

        ArrayList<String> snacks = new ArrayList<>();
        snacks.add("과자");
        snacks.add("사탕");
        snacks.add("초콜릿");
        snacks.add("젤리");
        snacks.add("과자");

        System.out.println("원본: " + snacks);

        // Iterator로 반복하면서 "과자" 삭제
        Iterator<String> it = snacks.iterator();
        while (it.hasNext()) {
            String snack = it.next();
            if (snack.equals("과자")) {
                it.remove();  // 안전하게 삭제!
            }
        }
        System.out.println("과자 삭제 후: " + snacks);

        System.out.println();

        // ═══════════════════════════════════════════════════
        //  섹션 9: Collections 유틸리티 클래스
        // ═══════════════════════════════════════════════════

        /*
         * Collections 클래스란?
         *
         * 컬렉션(List, Set, Map 등)을 다루는 도구 모음이에요!
         * Arrays 클래스처럼 유용한 메서드들이 많아요.
         */

        System.out.println("=== Collections 유틸리티 ===");

        ArrayList<Integer> numList = new ArrayList<>();
        for (int i = 1; i <= 8; i++) {
            numList.add(i);
        }
        System.out.println("원본: " + numList);

        // 정렬
        Collections.sort(numList);
        System.out.println("오름차순 정렬: " + numList);

        // 역순 정렬
        Collections.sort(numList, Collections.reverseOrder());
        System.out.println("내림차순 정렬: " + numList);

        // 섞기
        Collections.shuffle(numList);
        System.out.println("랜덤 섞기: " + numList);

        // 최대/최소값
        System.out.println("최대값: " + Collections.max(numList));
        System.out.println("최소값: " + Collections.min(numList));

        // 뒤집기
        Collections.sort(numList);
        System.out.println("정렬: " + numList);
        Collections.reverse(numList);
        System.out.println("뒤집기: " + numList);

        // 빈도수 세기
        ArrayList<String> colors = new ArrayList<>();
        colors.add("빨강"); colors.add("파랑"); colors.add("빨강");
        colors.add("초록"); colors.add("빨강"); colors.add("파랑");
        System.out.println("\n색상 빈도:");
        System.out.println("빨강 개수: " + Collections.frequency(colors, "빨강"));
        System.out.println("파랑 개수: " + Collections.frequency(colors, "파랑"));

        System.out.println();
        System.out.println("╔══════════════════════════════════════════╗");
        System.out.println("║  04단계 배열/컬렉션 학습 완료! 훌륭해요! ║");
        System.out.println("╚══════════════════════════════════════════╝");
    }
}
