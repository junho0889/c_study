/*
 * =============================================================================
 *  C++ 학습 19장: 자료구조 & 알고리즘 (Data Structures & Algorithms)
 * =============================================================================
 *
 *  이 파일은 C++로 핵심 자료구조와 알고리즘을 직접 구현하며 학습합니다.
 *  STL에 의존하지 않고 내부 원리를 깊이 이해하는 것이 목표입니다.
 *
 *  목차:
 *    레슨 1: 연결 리스트 (Linked List)
 *    레슨 2: 스택과 큐 직접 구현
 *    레슨 3: 이진 트리와 BST (Binary Search Tree)
 *    레슨 4: 해시 테이블 (Hash Table)
 *    레슨 5: 정렬 알고리즘 (Sorting Algorithms)
 *    레슨 6: 탐색 알고리즘 (Searching Algorithms)
 *    레슨 7: Big-O 표기법 정리 + 실전 연습문제
 *
 *  컴파일: g++ -std=c++17 -o data_structures main.cpp
 *  실행:   ./data_structures
 *
 * =============================================================================
 *
 *  ┌─────────────────────────────────────────────────────────────────┐
 *  │              시간 복잡도 총정리 (Big-O Cheat Sheet)              │
 *  ├──────────────────┬──────────┬──────────┬──────────┬────────────┤
 *  │  자료구조/연산    │  접근    │  탐색    │  삽입    │   삭제     │
 *  ├──────────────────┼──────────┼──────────┼──────────┼────────────┤
 *  │  배열 (Array)     │  O(1)    │  O(n)    │  O(n)    │   O(n)     │
 *  │  연결 리스트      │  O(n)    │  O(n)    │  O(1)*   │   O(1)*    │
 *  │  스택 (Stack)     │  O(n)    │  O(n)    │  O(1)    │   O(1)     │
 *  │  큐 (Queue)       │  O(n)    │  O(n)    │  O(1)    │   O(1)     │
 *  │  해시 테이블      │  N/A     │  O(1)†   │  O(1)†   │   O(1)†    │
 *  │  BST (균형)       │  O(logn) │  O(logn) │  O(logn) │   O(logn)  │
 *  │  BST (최악)       │  O(n)    │  O(n)    │  O(n)    │   O(n)     │
 *  ├──────────────────┴──────────┴──────────┴──────────┴────────────┤
 *  │  * 해당 위치를 이미 알고 있을 때   † 평균 시간 복잡도           │
 *  └─────────────────────────────────────────────────────────────────┘
 *
 *  ┌─────────────────────────────────────────────────────────────────┐
 *  │              정렬 알고리즘 시간 복잡도 비교                      │
 *  ├──────────────────┬──────────┬──────────┬──────────┬────────────┤
 *  │  알고리즘        │  최선    │  평균    │  최악    │  공간      │
 *  ├──────────────────┼──────────┼──────────┼──────────┼────────────┤
 *  │  버블 정렬       │  O(n)    │  O(n²)   │  O(n²)   │  O(1)      │
 *  │  선택 정렬       │  O(n²)   │  O(n²)   │  O(n²)   │  O(1)      │
 *  │  삽입 정렬       │  O(n)    │  O(n²)   │  O(n²)   │  O(1)      │
 *  │  병합 정렬       │  O(nlogn)│  O(nlogn)│  O(nlogn)│  O(n)      │
 *  │  퀵 정렬         │  O(nlogn)│  O(nlogn)│  O(n²)   │  O(logn)   │
 *  └──────────────────┴──────────┴──────────┴──────────┴────────────┘
 *
 * =============================================================================
 */

#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <functional>
#include <cassert>
#include <sstream>
#include <algorithm>
#include <list>
#include <unordered_set>

using namespace std;

// =============================================================================
// 레슨 1: 연결 리스트 (Linked List)
// =============================================================================
/*
 *  연결 리스트란?
 *  - 데이터와 포인터로 구성된 노드들이 체인처럼 연결된 자료구조
 *  - 배열과 달리 메모리가 연속적이지 않아도 됨
 *  - 삽입/삭제가 O(1)로 매우 빠름 (위치를 알고 있을 때)
 *
 *  단일 연결 리스트 (Singly Linked List):
 *  ┌──────┬──┐    ┌──────┬──┐    ┌──────┬──┐    ┌──────┬──────┐
 *  │  10  │──┼───>│  20  │──┼───>│  30  │──┼───>│  40  │ null │
 *  └──────┴──┘    └──────┴──┘    └──────┴──┘    └──────┴──────┘
 *    head                                           tail
 *
 *  이중 연결 리스트 (Doubly Linked List):
 *         ┌──────┬──┐       ┌──────┬──┐       ┌──────┬──────┐
 *  null<──┤  10  │──┼──────>│  20  │──┼──────>│  30  │ null │
 *         └──────┴──┘<──────┼──────┴──┘<──────┼──────┴──────┘
 *           head                                  tail
 */

namespace Lesson1 {

// --- 단일 연결 리스트 (Singly Linked List) ---
template <typename T>
class SinglyLinkedList {
private:
    // 노드 구조체: 데이터와 다음 노드 포인터
    struct Node {
        T data;         // 저장할 데이터
        Node* next;     // 다음 노드를 가리키는 포인터
        Node(T val) : data(val), next(nullptr) {}
    };

    Node* head;   // 리스트의 시작점
    int count;    // 노드 개수 추적

public:
    SinglyLinkedList() : head(nullptr), count(0) {}

    // 소멸자: 모든 노드 메모리 해제 (메모리 누수 방지!)
    ~SinglyLinkedList() {
        Node* current = head;
        while (current) {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }

    // 앞에 삽입 - O(1): 가장 빠른 삽입 방법
    void pushFront(T val) {
        Node* newNode = new Node(val);
        newNode->next = head;   // 새 노드가 기존 head를 가리킴
        head = newNode;         // head를 새 노드로 변경
        count++;
    }

    // 뒤에 삽입 - O(n): tail을 유지하면 O(1) 가능
    void pushBack(T val) {
        Node* newNode = new Node(val);
        if (!head) {
            head = newNode;     // 리스트가 비어있으면 head로 설정
        } else {
            Node* current = head;
            while (current->next) {   // 마지막 노드까지 이동
                current = current->next;
            }
            current->next = newNode;  // 마지막 노드 뒤에 연결
        }
        count++;
    }

    // 특정 위치에 삽입 - O(n): 위치까지 이동하는 시간
    void insertAt(int index, T val) {
        if (index < 0 || index > count) {
            cout << "  [오류] 인덱스 범위 초과!" << endl;
            return;
        }
        if (index == 0) { pushFront(val); return; }

        Node* newNode = new Node(val);
        Node* current = head;
        for (int i = 0; i < index - 1; i++) {
            current = current->next;    // 삽입 위치 직전까지 이동
        }
        newNode->next = current->next;  // 새 노드가 다음 노드를 가리킴
        current->next = newNode;        // 이전 노드가 새 노드를 가리킴
        count++;
    }

    // 앞에서 삭제 - O(1)
    void popFront() {
        if (!head) return;
        Node* temp = head;
        head = head->next;
        delete temp;
        count--;
    }

    // 값으로 삭제 - O(n): 해당 값을 찾아서 삭제
    bool remove(T val) {
        if (!head) return false;

        if (head->data == val) {
            popFront();
            return true;
        }

        Node* current = head;
        while (current->next && current->next->data != val) {
            current = current->next;
        }

        if (current->next) {
            Node* temp = current->next;
            current->next = temp->next;   // 삭제할 노드를 건너뛰고 연결
            delete temp;
            count--;
            return true;
        }
        return false;    // 값을 찾지 못함
    }

    // 검색 - O(n): 처음부터 순차적으로 탐색
    bool search(T val) const {
        Node* current = head;
        while (current) {
            if (current->data == val) return true;
            current = current->next;
        }
        return false;
    }

    // 리스트 출력
    void print() const {
        Node* current = head;
        cout << "  [";
        while (current) {
            cout << current->data;
            if (current->next) cout << " -> ";
            current = current->next;
        }
        cout << "]" << endl;
    }

    int size() const { return count; }
    bool empty() const { return head == nullptr; }

    // 리스트 뒤집기 - O(n): 면접 단골 문제!
    /*
     *  뒤집기 과정 (10 -> 20 -> 30):
     *
     *  prev=null, curr=10, next=20
     *  10의 next를 null로 변경    null <- 10   20 -> 30
     *
     *  prev=10, curr=20, next=30
     *  20의 next를 10으로 변경    null <- 10 <- 20   30
     *
     *  prev=20, curr=30, next=null
     *  30의 next를 20으로 변경    null <- 10 <- 20 <- 30
     *  head = 30
     */
    void reverse() {
        Node* prev = nullptr;
        Node* current = head;
        Node* next = nullptr;

        while (current) {
            next = current->next;     // 다음 노드 저장
            current->next = prev;     // 현재 노드의 방향을 뒤집음
            prev = current;           // prev를 현재로 이동
            current = next;           // current를 다음으로 이동
        }
        head = prev;                  // head를 마지막 노드로 변경
    }
};

// --- 이중 연결 리스트 (Doubly Linked List) ---
template <typename T>
class DoublyLinkedList {
private:
    struct Node {
        T data;
        Node* prev;    // 이전 노드 포인터 (단일과의 차이점!)
        Node* next;    // 다음 노드 포인터
        Node(T val) : data(val), prev(nullptr), next(nullptr) {}
    };

    Node* head;
    Node* tail;        // tail 포인터로 뒤에서의 접근이 O(1)
    int count;

public:
    DoublyLinkedList() : head(nullptr), tail(nullptr), count(0) {}

    ~DoublyLinkedList() {
        Node* current = head;
        while (current) {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }

    // 뒤에 삽입 - O(1): tail 포인터 덕분에 바로 접근 가능
    void pushBack(T val) {
        Node* newNode = new Node(val);
        if (!tail) {
            head = tail = newNode;
        } else {
            tail->next = newNode;
            newNode->prev = tail;
            tail = newNode;
        }
        count++;
    }

    // 앞에 삽입 - O(1)
    void pushFront(T val) {
        Node* newNode = new Node(val);
        if (!head) {
            head = tail = newNode;
        } else {
            newNode->next = head;
            head->prev = newNode;
            head = newNode;
        }
        count++;
    }

    // 뒤에서 삭제 - O(1): 이중 연결 리스트의 장점!
    void popBack() {
        if (!tail) return;
        Node* temp = tail;
        tail = tail->prev;
        if (tail) tail->next = nullptr;
        else head = nullptr;
        delete temp;
        count--;
    }

    // 양방향 출력
    void printForward() const {
        cout << "  정방향: [";
        Node* cur = head;
        while (cur) {
            cout << cur->data;
            if (cur->next) cout << " <-> ";
            cur = cur->next;
        }
        cout << "]" << endl;
    }

    void printBackward() const {
        cout << "  역방향: [";
        Node* cur = tail;
        while (cur) {
            cout << cur->data;
            if (cur->prev) cout << " <-> ";
            cur = cur->prev;
        }
        cout << "]" << endl;
    }

    int size() const { return count; }
};

void demo() {
    cout << "=== 레슨 1: 연결 리스트 (Linked List) ===" << endl << endl;

    // 단일 연결 리스트 테스트
    cout << "--- 단일 연결 리스트 ---" << endl;
    SinglyLinkedList<int> sll;
    sll.pushBack(10);
    sll.pushBack(20);
    sll.pushBack(30);
    sll.pushFront(5);
    cout << "  삽입 후: "; sll.print();

    sll.insertAt(2, 15);
    cout << "  인덱스 2에 15 삽입: "; sll.print();

    sll.remove(20);
    cout << "  20 삭제 후: "; sll.print();

    cout << "  15 검색: " << (sll.search(15) ? "찾음" : "없음") << endl;
    cout << "  99 검색: " << (sll.search(99) ? "찾음" : "없음") << endl;

    sll.reverse();
    cout << "  뒤집기 후: "; sll.print();

    // 이중 연결 리스트 테스트
    cout << endl << "--- 이중 연결 리스트 ---" << endl;
    DoublyLinkedList<string> dll;
    dll.pushBack("사과");
    dll.pushBack("바나나");
    dll.pushBack("체리");
    dll.pushFront("딸기");
    dll.printForward();
    dll.printBackward();

    dll.popBack();
    cout << "  뒤에서 삭제 후:" << endl;
    dll.printForward();
    cout << endl;
}

} // namespace Lesson1


// =============================================================================
// 레슨 2: 스택과 큐 직접 구현
// =============================================================================
/*
 *  스택 (Stack) - LIFO (Last In, First Out)
 *  ┌─────┐
 *  │  30 │  <- top (가장 나중에 들어온 것이 먼저 나감)
 *  ├─────┤
 *  │  20 │
 *  ├─────┤
 *  │  10 │
 *  └─────┘
 *
 *  큐 (Queue) - FIFO (First In, First Out)
 *  front ->  ┌────┬────┬────┬────┐  <- rear
 *            │ 10 │ 20 │ 30 │ 40 │
 *            └────┴────┴────┴────┘
 *            먼저 들어온 것이 먼저 나감
 */

namespace Lesson2 {

// --- 배열 기반 스택 ---
template <typename T, int MAX_SIZE = 100>
class ArrayStack {
private:
    T data[MAX_SIZE];   // 고정 크기 배열
    int topIndex;       // top 원소의 인덱스 (-1이면 비어있음)

public:
    ArrayStack() : topIndex(-1) {}

    void push(T val) {
        if (topIndex >= MAX_SIZE - 1) {
            cout << "  [오류] 스택 오버플로우!" << endl;
            return;
        }
        data[++topIndex] = val;   // 인덱스 증가 후 저장
    }

    T pop() {
        if (empty()) {
            throw runtime_error("스택이 비어있습니다!");
        }
        return data[topIndex--];  // 값 반환 후 인덱스 감소
    }

    T top() const {
        if (topIndex < 0) throw runtime_error("스택이 비어있습니다!");
        return data[topIndex];
    }

    bool empty() const { return topIndex < 0; }
    int size() const { return topIndex + 1; }
};

// --- 연결 리스트 기반 큐 ---
template <typename T>
class LinkedQueue {
private:
    struct Node {
        T data;
        Node* next;
        Node(T val) : data(val), next(nullptr) {}
    };

    Node* front;    // 앞 (dequeue할 위치)
    Node* rear;     // 뒤 (enqueue할 위치)
    int count;

public:
    LinkedQueue() : front(nullptr), rear(nullptr), count(0) {}

    ~LinkedQueue() {
        while (front) {
            Node* temp = front;
            front = front->next;
            delete temp;
        }
    }

    // 뒤에 삽입 - O(1)
    void enqueue(T val) {
        Node* newNode = new Node(val);
        if (!rear) {
            front = rear = newNode;
        } else {
            rear->next = newNode;
            rear = newNode;
        }
        count++;
    }

    // 앞에서 제거 - O(1)
    T dequeue() {
        if (empty()) throw runtime_error("큐가 비어있습니다!");
        Node* temp = front;
        T val = temp->data;
        front = front->next;
        if (!front) rear = nullptr;   // 마지막 원소 제거 시
        delete temp;
        count--;
        return val;
    }

    T peek() const {
        if (!front) throw runtime_error("큐가 비어있습니다!");
        return front->data;
    }

    bool empty() const { return front == nullptr; }
    int size() const { return count; }
};

// --- 실전 활용 1: 괄호 검사 (스택의 대표적 활용) ---
/*
 *  유효한 괄호 문자열인지 검사
 *  "(())"  -> 유효
 *  "({[]})" -> 유효
 *  "(]"    -> 무효
 *  "(()"   -> 무효
 */
bool isValidParentheses(const string& s) {
    ArrayStack<char> stack;
    for (char c : s) {
        if (c == '(' || c == '{' || c == '[') {
            stack.push(c);   // 여는 괄호는 스택에 push
        } else {
            if (stack.empty()) return false;  // 닫는 괄호인데 스택이 비어있음
            char top = stack.pop();
            // 짝이 맞는지 확인
            if ((c == ')' && top != '(') ||
                (c == '}' && top != '{') ||
                (c == ']' && top != '[')) {
                return false;
            }
        }
    }
    return stack.empty();   // 스택이 비어있어야 모든 괄호가 짝이 맞음
}

void demo() {
    cout << "=== 레슨 2: 스택과 큐 직접 구현 ===" << endl << endl;

    // 스택 테스트
    cout << "--- 배열 기반 스택 ---" << endl;
    ArrayStack<int> stack;
    stack.push(10); stack.push(20); stack.push(30);
    cout << "  top: " << stack.top() << endl;
    cout << "  pop: " << stack.pop() << ", " << stack.pop() << endl;
    cout << "  크기: " << stack.size() << endl;

    // 큐 테스트
    cout << endl << "--- 연결 리스트 기반 큐 ---" << endl;
    LinkedQueue<string> q;
    q.enqueue("첫번째");
    q.enqueue("두번째");
    q.enqueue("세번째");
    cout << "  dequeue: " << q.dequeue() << endl;
    cout << "  peek: " << q.peek() << endl;
    cout << "  크기: " << q.size() << endl;

    // 괄호 검사
    cout << endl << "--- 괄호 검사 (스택 활용) ---" << endl;
    vector<string> tests = {"(())", "({[]})", "(]", "(()", "{[]}"};
    for (auto& t : tests) {
        cout << "  \"" << t << "\" -> "
             << (isValidParentheses(t) ? "유효" : "무효") << endl;
    }
    cout << endl;
}

} // namespace Lesson2


// =============================================================================
// 레슨 3: 이진 트리와 BST (Binary Search Tree)
// =============================================================================
/*
 *  이진 탐색 트리 (BST) 규칙:
 *  - 왼쪽 서브트리의 모든 값 < 현재 노드 값
 *  - 오른쪽 서브트리의 모든 값 > 현재 노드 값
 *
 *              50
 *            /    \
 *          30      70
 *         /  \    /  \
 *       20   40  60   80
 *
 *  순회 방법:
 *  - 전위 (Preorder):  루트 -> 왼 -> 오  =>  50,30,20,40,70,60,80
 *  - 중위 (Inorder):   왼 -> 루트 -> 오  =>  20,30,40,50,60,70,80  (정렬!)
 *  - 후위 (Postorder): 왼 -> 오 -> 루트  =>  20,40,30,60,80,70,50
 *  - 레벨 (Level):     BFS 순서          =>  50,30,70,20,40,60,80
 */

namespace Lesson3 {

template <typename T>
class BST {
private:
    struct Node {
        T data;
        Node* left;
        Node* right;
        Node(T val) : data(val), left(nullptr), right(nullptr) {}
    };

    Node* root;

    // 재귀적 삽입: 적절한 위치를 찾아 삽입
    Node* insert(Node* node, T val) {
        if (!node) return new Node(val);

        if (val < node->data)
            node->left = insert(node->left, val);    // 작으면 왼쪽으로
        else if (val > node->data)
            node->right = insert(node->right, val);  // 크면 오른쪽으로
        // 같으면 무시 (중복 허용 안 함)
        return node;
    }

    // 중위 순회 (정렬된 순서 출력)
    void inorder(Node* node) const {
        if (!node) return;
        inorder(node->left);
        cout << node->data << " ";
        inorder(node->right);
    }

    // 전위 순회 (트리 복사에 유용)
    void preorder(Node* node) const {
        if (!node) return;
        cout << node->data << " ";
        preorder(node->left);
        preorder(node->right);
    }

    // 후위 순회 (트리 삭제에 유용)
    void postorder(Node* node) const {
        if (!node) return;
        postorder(node->left);
        postorder(node->right);
        cout << node->data << " ";
    }

    // 검색 - O(log n) 평균, O(n) 최악
    bool search(Node* node, T val) const {
        if (!node) return false;
        if (val == node->data) return true;
        if (val < node->data) return search(node->left, val);
        return search(node->right, val);
    }

    // 최솟값 찾기: 가장 왼쪽 노드
    Node* findMin(Node* node) const {
        while (node->left) node = node->left;
        return node;
    }

    // 삭제: 세 가지 경우를 처리
    /*
     *  경우 1: 리프 노드 (자식 없음) -> 그냥 삭제
     *  경우 2: 자식 하나 -> 자식으로 대체
     *  경우 3: 자식 둘 -> 중위 후속자(오른쪽 서브트리의 최솟값)로 대체
     *
     *  경우 3 예시 (50 삭제):
     *          50               60
     *        /    \    =>     /    \
     *      30      70       30      70
     *             /  \             /  \
     *           60   80         65   80
     *            \
     *            65
     */
    Node* remove(Node* node, T val) {
        if (!node) return nullptr;

        if (val < node->data) {
            node->left = remove(node->left, val);
        } else if (val > node->data) {
            node->right = remove(node->right, val);
        } else {
            // 찾은 경우
            if (!node->left) {
                // 경우 1,2: 왼쪽 자식 없음
                Node* temp = node->right;
                delete node;
                return temp;
            } else if (!node->right) {
                // 경우 2: 오른쪽 자식 없음
                Node* temp = node->left;
                delete node;
                return temp;
            }
            // 경우 3: 자식 둘 다 있음
            Node* successor = findMin(node->right);
            node->data = successor->data;
            node->right = remove(node->right, successor->data);
        }
        return node;
    }

    // 트리 높이 계산
    int height(Node* node) const {
        if (!node) return -1;
        return 1 + max(height(node->left), height(node->right));
    }

    // 메모리 해제
    void destroy(Node* node) {
        if (!node) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

public:
    BST() : root(nullptr) {}
    ~BST() { destroy(root); }

    void insert(T val) { root = insert(root, val); }
    bool search(T val) const { return search(root, val); }
    void remove(T val) { root = remove(root, val); }
    int height() const { return height(root); }

    void printInorder() const { cout << "  중위: "; inorder(root); cout << endl; }
    void printPreorder() const { cout << "  전위: "; preorder(root); cout << endl; }
    void printPostorder() const { cout << "  후위: "; postorder(root); cout << endl; }

    // 레벨 순회 (BFS) - 큐 활용!
    void printLevelOrder() const {
        if (!root) return;
        cout << "  레벨: ";
        queue<Node*> q;
        q.push(root);
        while (!q.empty()) {
            Node* cur = q.front();
            q.pop();
            cout << cur->data << " ";
            if (cur->left) q.push(cur->left);
            if (cur->right) q.push(cur->right);
        }
        cout << endl;
    }
};

void demo() {
    cout << "=== 레슨 3: 이진 트리와 BST ===" << endl << endl;

    BST<int> tree;
    // 위의 ASCII 트리 구조와 동일하게 삽입
    for (int val : {50, 30, 70, 20, 40, 60, 80}) {
        tree.insert(val);
    }

    cout << "--- 순회 결과 ---" << endl;
    tree.printInorder();     // 정렬된 순서
    tree.printPreorder();
    tree.printPostorder();
    tree.printLevelOrder();  // BFS 순서

    cout << endl << "--- 검색 ---" << endl;
    cout << "  40 검색: " << (tree.search(40) ? "찾음" : "없음") << endl;
    cout << "  45 검색: " << (tree.search(45) ? "찾음" : "없음") << endl;

    cout << endl << "--- 삭제 ---" << endl;
    cout << "  높이: " << tree.height() << endl;
    tree.remove(30);
    cout << "  30 삭제 후 중위: ";
    tree.printInorder();
    cout << endl;
}

} // namespace Lesson3


// =============================================================================
// 레슨 4: 해시 테이블 (Hash Table)
// =============================================================================
/*
 *  해시 테이블: 키-값 쌍을 O(1)에 저장/검색하는 자료구조
 *
 *  동작 원리:
 *  키 -> 해시 함수 -> 인덱스 -> 배열 슬롯에 저장
 *
 *  충돌 해결 방법 1: 체이닝 (Chaining)
 *  ┌─────┐
 *  │  0  │ -> [김철수, 02-1234] -> [이영희, 02-5678]
 *  ├─────┤
 *  │  1  │ -> [박지민, 02-9012]
 *  ├─────┤
 *  │  2  │ -> null
 *  ├─────┤
 *  │  3  │ -> [최수진, 02-3456] -> [한민수, 02-7890]
 *  ├─────┤
 *  │  4  │ -> null
 *  └─────┘
 *
 *  충돌 해결 방법 2: 오픈 어드레싱 (선형 탐사)
 *  - 충돌 시 다음 빈 슬롯을 찾아 저장
 *  ┌─────┬─────────────┐
 *  │  0  │ (key1, val) │  <- hash(key1) = 0
 *  ├─────┼─────────────┤
 *  │  1  │ (key3, val) │  <- hash(key3) = 0 이지만 충돌! -> 1로 이동
 *  ├─────┼─────────────┤
 *  │  2  │   비어있음   │
 *  ├─────┼─────────────┤
 *  │  3  │ (key2, val) │  <- hash(key2) = 3
 *  └─────┴─────────────┘
 */

namespace Lesson4 {

// --- 체이닝 방식 해시 테이블 ---
class ChainingHashTable {
private:
    static const int TABLE_SIZE = 10;

    struct Entry {
        string key;
        string value;
        Entry* next;
        Entry(string k, string v) : key(k), value(v), next(nullptr) {}
    };

    Entry* table[TABLE_SIZE];
    int count;

    // 해시 함수: 문자열의 각 문자 ASCII 값을 활용
    int hashFunction(const string& key) const {
        unsigned long hash = 0;
        for (char c : key) {
            hash = hash * 31 + c;   // 31은 소수 - 좋은 분포를 만듦
        }
        return hash % TABLE_SIZE;
    }

public:
    ChainingHashTable() : count(0) {
        for (int i = 0; i < TABLE_SIZE; i++)
            table[i] = nullptr;
    }

    ~ChainingHashTable() {
        for (int i = 0; i < TABLE_SIZE; i++) {
            Entry* cur = table[i];
            while (cur) {
                Entry* next = cur->next;
                delete cur;
                cur = next;
            }
        }
    }

    // 삽입/업데이트 - 평균 O(1)
    void put(const string& key, const string& value) {
        int idx = hashFunction(key);
        Entry* cur = table[idx];

        // 키가 이미 존재하면 값 업데이트
        while (cur) {
            if (cur->key == key) {
                cur->value = value;
                return;
            }
            cur = cur->next;
        }

        // 새 엔트리를 체인 앞에 삽입
        Entry* newEntry = new Entry(key, value);
        newEntry->next = table[idx];
        table[idx] = newEntry;
        count++;
    }

    // 검색 - 평균 O(1)
    string get(const string& key) const {
        int idx = hashFunction(key);
        Entry* cur = table[idx];
        while (cur) {
            if (cur->key == key) return cur->value;
            cur = cur->next;
        }
        return "[키를 찾을 수 없음]";
    }

    // 삭제 - 평균 O(1)
    bool remove(const string& key) {
        int idx = hashFunction(key);
        Entry* cur = table[idx];
        Entry* prev = nullptr;

        while (cur) {
            if (cur->key == key) {
                if (prev) prev->next = cur->next;
                else table[idx] = cur->next;
                delete cur;
                count--;
                return true;
            }
            prev = cur;
            cur = cur->next;
        }
        return false;
    }

    // 내부 상태 시각화
    void printTable() const {
        for (int i = 0; i < TABLE_SIZE; i++) {
            cout << "  [" << i << "] ";
            Entry* cur = table[i];
            if (!cur) {
                cout << "(비어있음)";
            }
            while (cur) {
                cout << "{" << cur->key << ":" << cur->value << "}";
                if (cur->next) cout << " -> ";
                cur = cur->next;
            }
            cout << endl;
        }
    }

    int size() const { return count; }
};

void demo() {
    cout << "=== 레슨 4: 해시 테이블 ===" << endl << endl;

    ChainingHashTable ht;
    ht.put("apple", "사과");
    ht.put("banana", "바나나");
    ht.put("cherry", "체리");
    ht.put("date", "대추");
    ht.put("elderberry", "엘더베리");
    ht.put("fig", "무화과");
    ht.put("grape", "포도");

    cout << "--- 해시 테이블 내부 상태 ---" << endl;
    ht.printTable();

    cout << endl << "--- 검색 ---" << endl;
    cout << "  apple: " << ht.get("apple") << endl;
    cout << "  grape: " << ht.get("grape") << endl;
    cout << "  melon: " << ht.get("melon") << endl;

    ht.remove("banana");
    cout << endl << "  banana 삭제 후:" << endl;
    cout << "  banana: " << ht.get("banana") << endl;
    cout << "  현재 크기: " << ht.size() << endl;
    cout << endl;
}

} // namespace Lesson4


// =============================================================================
// 레슨 5: 정렬 알고리즘 (Sorting Algorithms)
// =============================================================================
/*
 *  정렬 알고리즘 시각화:
 *
 *  버블 정렬: 인접한 두 원소를 비교하여 교환 (거품처럼 위로 올라감)
 *  [5, 3, 8, 1]  ->  [3, 5, 1, 8]  ->  [3, 1, 5, 8]  ->  [1, 3, 5, 8]
 *
 *  병합 정렬: 분할 정복 (Divide and Conquer)
 *         [38, 27, 43, 3]
 *        /                \
 *   [38, 27]           [43, 3]         <- 분할
 *    /    \             /    \
 *  [38]  [27]        [43]   [3]        <- 분할
 *    \    /             \    /
 *   [27, 38]           [3, 43]         <- 병합
 *        \                /
 *       [3, 27, 38, 43]               <- 병합
 */

namespace Lesson5 {

// 배열 출력 헬퍼
void printArray(const vector<int>& arr, const string& label = "") {
    if (!label.empty()) cout << "  " << label << ": ";
    cout << "[";
    for (size_t i = 0; i < arr.size(); i++) {
        cout << arr[i];
        if (i < arr.size() - 1) cout << ", ";
    }
    cout << "]" << endl;
}

// --- 버블 정렬 O(n^2) ---
// 가장 단순하지만 가장 느린 정렬. 학습용으로 좋음
vector<int> bubbleSort(vector<int> arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        bool swapped = false;   // 최적화: 교환 없으면 이미 정렬됨
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) break;    // O(n) 최선 시간 달성
    }
    return arr;
}

// --- 선택 정렬 O(n^2) ---
// 매번 최솟값을 찾아 앞으로 이동
vector<int> selectionSort(vector<int> arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minIdx]) {
                minIdx = j;             // 최솟값 인덱스 갱신
            }
        }
        swap(arr[i], arr[minIdx]);      // 최솟값을 현재 위치로
    }
    return arr;
}

// --- 삽입 정렬 O(n^2) ---
// 카드를 손에 정리하는 것처럼, 하나씩 올바른 위치에 삽입
vector<int> insertionSort(vector<int> arr) {
    int n = arr.size();
    for (int i = 1; i < n; i++) {
        int key = arr[i];               // 삽입할 원소
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];        // 큰 원소를 오른쪽으로 밀기
            j--;
        }
        arr[j + 1] = key;              // 올바른 위치에 삽입
    }
    return arr;
}

// --- 병합 정렬 O(n log n) ---
// 가장 안정적인 정렬. 항상 O(n log n) 보장
void merge(vector<int>& arr, int left, int mid, int right) {
    vector<int> leftArr(arr.begin() + left, arr.begin() + mid + 1);
    vector<int> rightArr(arr.begin() + mid + 1, arr.begin() + right + 1);

    int i = 0, j = 0, k = left;

    // 두 배열을 비교하며 병합
    while (i < (int)leftArr.size() && j < (int)rightArr.size()) {
        if (leftArr[i] <= rightArr[j]) {
            arr[k++] = leftArr[i++];
        } else {
            arr[k++] = rightArr[j++];
        }
    }

    // 남은 원소 복사
    while (i < (int)leftArr.size()) arr[k++] = leftArr[i++];
    while (j < (int)rightArr.size()) arr[k++] = rightArr[j++];
}

void mergeSortHelper(vector<int>& arr, int left, int right) {
    if (left >= right) return;
    int mid = left + (right - left) / 2;   // 오버플로 방지
    mergeSortHelper(arr, left, mid);         // 왼쪽 반 정렬
    mergeSortHelper(arr, mid + 1, right);    // 오른쪽 반 정렬
    merge(arr, left, mid, right);            // 병합
}

vector<int> mergeSort(vector<int> arr) {
    if (arr.size() <= 1) return arr;
    mergeSortHelper(arr, 0, arr.size() - 1);
    return arr;
}

// --- 퀵 정렬 O(n log n) 평균 ---
// 피벗을 기준으로 작은 것/큰 것으로 분할
int partition(vector<int>& arr, int low, int high) {
    int pivot = arr[high];   // 마지막 원소를 피벗으로 선택
    int i = low - 1;         // 작은 원소들의 마지막 인덱스

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr[i], arr[j]);   // 작은 원소를 앞으로
        }
    }
    swap(arr[i + 1], arr[high]);    // 피벗을 올바른 위치로
    return i + 1;                    // 피벗의 최종 위치
}

void quickSortHelper(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pivotIdx = partition(arr, low, high);
        quickSortHelper(arr, low, pivotIdx - 1);    // 피벗 왼쪽
        quickSortHelper(arr, pivotIdx + 1, high);   // 피벗 오른쪽
    }
}

vector<int> quickSort(vector<int> arr) {
    if (arr.size() <= 1) return arr;
    quickSortHelper(arr, 0, arr.size() - 1);
    return arr;
}

void demo() {
    cout << "=== 레슨 5: 정렬 알고리즘 ===" << endl << endl;

    vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    printArray(data, "원본 배열");
    cout << endl;

    printArray(bubbleSort(data), "버블 정렬");
    printArray(selectionSort(data), "선택 정렬");
    printArray(insertionSort(data), "삽입 정렬");
    printArray(mergeSort(data), "병합 정렬");
    printArray(quickSort(data), "퀵 정렬  ");
    cout << endl;
}

} // namespace Lesson5


// =============================================================================
// 레슨 6: 탐색 알고리즘 (Search Algorithms)
// =============================================================================
/*
 *  이진 탐색 (Binary Search) - O(log n)
 *  전제: 배열이 정렬되어 있어야 함
 *
 *  [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]  목표: 23
 *
 *  1단계: mid=16, 23 > 16 -> 오른쪽 반
 *         [2, 5, 8, 12, 16, |23, 38, 56, 72, 91]
 *
 *  2단계: mid=56, 23 < 56 -> 왼쪽 반
 *         [23, 38, |56, 72, 91]
 *
 *  3단계: mid=23, 찾았다!
 *
 *  그래프 탐색:
 *  DFS (깊이 우선 탐색) - 스택/재귀 사용
 *       A
 *      / \
 *     B   C        DFS: A -> B -> D -> E -> C -> F
 *    / \   \       BFS: A -> B -> C -> D -> E -> F
 *   D   E   F
 */

namespace Lesson6 {

// --- 이진 탐색 (반복문 버전) ---
int binarySearch(const vector<int>& arr, int target) {
    int left = 0, right = arr.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;  // 오버플로 방지

        if (arr[mid] == target)
            return mid;              // 찾았다!
        else if (arr[mid] < target)
            left = mid + 1;          // 오른쪽 반 탐색
        else
            right = mid - 1;         // 왼쪽 반 탐색
    }
    return -1;  // 찾지 못함
}

// --- 이진 탐색 (재귀 버전) ---
int binarySearchRecursive(const vector<int>& arr, int target, int left, int right) {
    if (left > right) return -1;

    int mid = left + (right - left) / 2;
    if (arr[mid] == target) return mid;
    if (arr[mid] < target)
        return binarySearchRecursive(arr, target, mid + 1, right);
    return binarySearchRecursive(arr, target, left, mid - 1);
}

// --- 그래프 (인접 리스트 표현) ---
/*
 *  그래프 표현 방법:
 *
 *  인접 리스트:                    인접 행렬:
 *  0: [1, 2]                      0  1  2  3  4
 *  1: [0, 3, 4]              0 [  0  1  1  0  0 ]
 *  2: [0, 4]                 1 [  1  0  0  1  1 ]
 *  3: [1]                    2 [  1  0  0  0  1 ]
 *  4: [1, 2]                 3 [  0  1  0  0  0 ]
 *                            4 [  0  1  1  0  0 ]
 */
class Graph {
private:
    int vertices;
    vector<vector<int>> adj;   // 인접 리스트

public:
    Graph(int v) : vertices(v), adj(v) {}

    void addEdge(int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);    // 무방향 그래프
    }

    // --- DFS (깊이 우선 탐색) - 재귀 ---
    void dfsHelper(int node, vector<bool>& visited) {
        visited[node] = true;
        cout << node << " ";

        for (int neighbor : adj[node]) {
            if (!visited[neighbor]) {
                dfsHelper(neighbor, visited);
            }
        }
    }

    void dfs(int start) {
        vector<bool> visited(vertices, false);
        cout << "  DFS (" << start << "에서 시작): ";
        dfsHelper(start, visited);
        cout << endl;
    }

    // --- BFS (너비 우선 탐색) - 큐 사용 ---
    void bfs(int start) {
        vector<bool> visited(vertices, false);
        queue<int> q;

        visited[start] = true;
        q.push(start);

        cout << "  BFS (" << start << "에서 시작): ";
        while (!q.empty()) {
            int node = q.front();
            q.pop();
            cout << node << " ";

            for (int neighbor : adj[node]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    q.push(neighbor);
                }
            }
        }
        cout << endl;
    }
};

void demo() {
    cout << "=== 레슨 6: 탐색 알고리즘 ===" << endl << endl;

    // 이진 탐색
    cout << "--- 이진 탐색 ---" << endl;
    vector<int> sorted = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
    cout << "  배열: [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]" << endl;

    int idx = binarySearch(sorted, 23);
    cout << "  23 탐색 -> 인덱스: " << idx << endl;

    idx = binarySearch(sorted, 50);
    cout << "  50 탐색 -> 인덱스: " << idx << " (없음)" << endl;

    idx = binarySearchRecursive(sorted, 72, 0, sorted.size() - 1);
    cout << "  72 탐색 (재귀) -> 인덱스: " << idx << endl;

    // 그래프 탐색
    cout << endl << "--- 그래프 탐색 (DFS/BFS) ---" << endl;
    cout << "  그래프 구조:" << endl;
    cout << "    0 --- 1 --- 3" << endl;
    cout << "    |   / |" << endl;
    cout << "    |  /  |" << endl;
    cout << "    2 --- 4" << endl;
    cout << endl;

    Graph g(5);
    g.addEdge(0, 1);
    g.addEdge(0, 2);
    g.addEdge(1, 3);
    g.addEdge(1, 4);
    g.addEdge(2, 4);

    g.dfs(0);
    g.bfs(0);
    cout << endl;
}

} // namespace Lesson6


// =============================================================================
// 레슨 7: Big-O 표기법 정리 + 실전 연습문제
// =============================================================================
/*
 *  Big-O 성장률 비교 (n=1000 기준):
 *
 *  시간 |
 *  복잡 |  O(n!)
 *  도   |  /
 *       | /    O(2^n)
 *       |/     /
 *       |     /  O(n^2)
 *       |    /   /
 *       |   /   /    O(n log n)
 *       |  /   /     /
 *       | /   /    _/     O(n)
 *       |/   /   _/      /
 *       |   / __/       /      O(log n)
 *       |  /_/         /      _____
 *       | /           /  ____/          O(1)
 *       |/___________/___________-----------___
 *       +──────────────────────────────────────> n
 *
 *  O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n) < O(n!)
 *
 *  실전 예시:
 *  O(1)      : 배열 인덱스 접근, 해시 테이블 검색
 *  O(log n)  : 이진 탐색
 *  O(n)      : 선형 탐색, 연결 리스트 순회
 *  O(n log n): 병합 정렬, 퀵 정렬 (평균)
 *  O(n^2)    : 버블 정렬, 이중 for문
 *  O(2^n)    : 피보나치 (재귀, 메모이제이션 없이)
 */

namespace Lesson7 {

// --- 실전 문제 1: 배열에서 중복 찾기 ---
/*
 *  방법 1: 이중 루프 - O(n^2)
 *  방법 2: 정렬 후 인접 비교 - O(n log n)
 *  방법 3: 해시 셋 사용 - O(n)  <- 최적!
 */

// O(n^2) 풀이 - 브루트 포스
bool hasDuplicate_BruteForce(const vector<int>& arr) {
    for (size_t i = 0; i < arr.size(); i++) {
        for (size_t j = i + 1; j < arr.size(); j++) {
            if (arr[i] == arr[j]) return true;
        }
    }
    return false;
}

// O(n) 풀이 - 해시 셋
bool hasDuplicate_HashSet(const vector<int>& arr) {
    unordered_set<int> seen;
    for (int num : arr) {
        if (seen.count(num)) return true;  // 이미 본 숫자
        seen.insert(num);
    }
    return false;
}

// --- 실전 문제 2: 두 수의 합 (Two Sum) ---
/*
 *  배열에서 합이 target인 두 수의 인덱스를 찾아라
 *
 *  예: nums = [2, 7, 11, 15], target = 9
 *  답: [0, 1] (nums[0] + nums[1] = 2 + 7 = 9)
 *
 *  핵심 아이디어: target - nums[i]가 해시맵에 있는지 확인
 *  num=2일 때: 9-2=7, 맵에 7 없음 -> 맵에 {2:0} 저장
 *  num=7일 때: 9-7=2, 맵에 2 있음! -> [0, 1] 반환
 */
pair<int, int> twoSum(const vector<int>& nums, int target) {
    unordered_map<int, int> numMap;   // 값 -> 인덱스

    for (int i = 0; i < (int)nums.size(); i++) {
        int complement = target - nums[i];
        auto it = numMap.find(complement);
        if (it != numMap.end()) {
            return {it->second, i};   // 찾았다!
        }
        numMap[nums[i]] = i;
    }
    return {-1, -1};   // 찾지 못함
}

// --- 실전 문제 3: 최대 부분 배열 합 (Kadane's Algorithm) ---
/*
 *  연속된 부분 배열의 최대 합을 구하라 - O(n)
 *
 *  예: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
 *  답: 6 (부분 배열 [4, -1, 2, 1])
 *
 *  핵심: 현재까지의 최대 합이 음수면 버리고 새로 시작
 */
int maxSubarraySum(const vector<int>& nums) {
    int maxSum = nums[0];
    int currentSum = nums[0];

    for (size_t i = 1; i < nums.size(); i++) {
        // 현재 합에 추가하는 것과 새로 시작하는 것 중 큰 것 선택
        currentSum = max(nums[i], currentSum + nums[i]);
        maxSum = max(maxSum, currentSum);
    }
    return maxSum;
}

// --- 실전 문제 4: 문자열 뒤집기 (in-place) ---
// O(n) 시간, O(1) 공간
void reverseString(string& s) {
    int left = 0, right = s.size() - 1;
    while (left < right) {
        swap(s[left], s[right]);
        left++;
        right--;
    }
}

// --- 실전 문제 5: 피보나치 (메모이제이션) ---
/*
 *  일반 재귀: O(2^n) - 매우 느림!
 *  메모이제이션: O(n) - 중복 계산 제거
 *
 *  일반 재귀 호출 트리 (fib(5)):
 *                fib(5)
 *               /      \
 *          fib(4)      fib(3)        <- fib(3) 중복 계산!
 *          /    \       /   \
 *      fib(3) fib(2) fib(2) fib(1)
 *      /   \
 *  fib(2) fib(1)
 */
long long fibMemo(int n, vector<long long>& memo) {
    if (n <= 1) return n;
    if (memo[n] != -1) return memo[n];  // 이미 계산한 값 재사용
    memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    return memo[n];
}

long long fibonacci(int n) {
    vector<long long> memo(n + 1, -1);
    return fibMemo(n, memo);
}

void demo() {
    cout << "=== 레슨 7: Big-O 정리 + 실전 연습문제 ===" << endl << endl;

    // 문제 1: 중복 찾기
    cout << "--- 문제 1: 배열 중복 찾기 ---" << endl;
    vector<int> arr1 = {1, 3, 5, 7, 9};
    vector<int> arr2 = {1, 3, 5, 3, 9};
    cout << "  [1,3,5,7,9] 중복: "
         << (hasDuplicate_HashSet(arr1) ? "있음" : "없음") << endl;
    cout << "  [1,3,5,3,9] 중복: "
         << (hasDuplicate_HashSet(arr2) ? "있음" : "없음") << endl;

    // 문제 2: 두 수의 합
    cout << endl << "--- 문제 2: 두 수의 합 ---" << endl;
    vector<int> nums = {2, 7, 11, 15};
    auto [i, j] = twoSum(nums, 9);
    cout << "  [2,7,11,15], target=9 -> 인덱스 [" << i << ", " << j << "]" << endl;
    auto [a, b] = twoSum(nums, 18);
    cout << "  [2,7,11,15], target=18 -> 인덱스 [" << a << ", " << b << "]" << endl;

    // 문제 3: 최대 부분 배열 합
    cout << endl << "--- 문제 3: 최대 부분 배열 합 (Kadane) ---" << endl;
    vector<int> subArr = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
    cout << "  [-2,1,-3,4,-1,2,1,-5,4] -> 최대 합: "
         << maxSubarraySum(subArr) << endl;

    // 문제 4: 문자열 뒤집기
    cout << endl << "--- 문제 4: 문자열 뒤집기 ---" << endl;
    string str = "Hello, World!";
    cout << "  원본: " << str << endl;
    reverseString(str);
    cout << "  뒤집기: " << str << endl;

    // 문제 5: 피보나치
    cout << endl << "--- 문제 5: 피보나치 (메모이제이션) ---" << endl;
    for (int n : {5, 10, 20, 40}) {
        cout << "  fib(" << n << ") = " << fibonacci(n) << endl;
    }

    // Big-O 요약
    cout << endl;
    cout << "  ┌──────────────────────────────────────────────┐" << endl;
    cout << "  │           학습 포인트 요약                     │" << endl;
    cout << "  ├──────────────────────────────────────────────┤" << endl;
    cout << "  │  1. 자료구조 선택이 알고리즘 성능을 결정한다  │" << endl;
    cout << "  │  2. 해시 테이블은 O(1) 탐색의 핵심 도구      │" << endl;
    cout << "  │  3. 분할 정복은 O(n log n)의 비밀             │" << endl;
    cout << "  │  4. 공간-시간 트레이드오프를 항상 고려하라    │" << endl;
    cout << "  │  5. 면접에서는 최적 시간복잡도를 항상 물어본다│" << endl;
    cout << "  └──────────────────────────────────────────────┘" << endl;
    cout << endl;
}

} // namespace Lesson7


// =============================================================================
// 메인 함수: 모든 레슨 실행
// =============================================================================
/*
=============================================================================
  레슨별 demo() 출력 흐름 가이드 (대략)
=============================================================================
  Lesson1 (LinkedList):
    push_front(10), push_front(20), push_front(30)
    → 리스트: [30 → 20 → 10]
    push_back(40) → [30 → 20 → 10 → 40]
    remove(20)    → [30 → 10 → 40]
    size = 3

  Lesson2 (Stack/Queue):
    Stack push 1,2,3 → top=3 → pop=3 → top=2 → pop=2 → top=1
    Queue enqueue 1,2,3 → front=1 → dequeue=1 → front=2

  Lesson3 (BST):
    insert 50, 30, 70, 20, 40, 60, 80
    inorder 순회: 20 30 40 50 60 70 80 (정렬됨)
    min=20, max=80
    search(40) → found
    remove(50) → 트리 재구조화

  Lesson4 (HashTable):
    insert ("apple",1), ("banana",2), ("cherry",3)
    get("banana") → 2
    충돌 시뮬레이션: 같은 버킷에 chain

  Lesson5 (정렬):
    입력: [64, 34, 25, 12, 22, 11, 90]
    버블/선택/삽입/병합/퀵 정렬 모두 → [11, 12, 22, 25, 34, 64, 90]

  Lesson6 (탐색):
    선형 탐색: O(n), 정렬 안 된 데이터
    이진 탐색: O(log n), 정렬된 데이터에서 빠름
    7 찾기 → index 3 (정렬된 [1,3,5,7,9])

  Lesson7 (Big-O 정리): 표 출력
=============================================================================
*/

int main() {
    cout << "================================================================" << endl;
    cout << "  C++ 학습 19장: 자료구조 & 알고리즘" << endl;
    cout << "  Data Structures & Algorithms" << endl;
    cout << "================================================================" << endl;
    cout << endl;

    Lesson1::demo();   // 연결 리스트
    Lesson2::demo();   // 스택/큐
    Lesson3::demo();   // BST
    Lesson4::demo();   // 해시 테이블
    Lesson5::demo();   // 정렬
    Lesson6::demo();   // 탐색
    Lesson7::demo();   // Big-O 정리

    cout << "================================================================" << endl;
    cout << "  19장 학습 완료!" << endl;
    cout << "  다음 단계: 20_advanced_oop (고급 OOP)" << endl;
    cout << "================================================================" << endl;

    return 0;
}
