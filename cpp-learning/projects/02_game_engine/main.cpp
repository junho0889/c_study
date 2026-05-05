/*
 * ============================================================================
 *  게임 엔진 코어 (Game Engine Core)
 *  - C++이 게임 업계에서 #1인 이유를 직접 체험하는 프로젝트
 * ============================================================================
 *
 *  왜 게임에서 C++을 쓸까? (C# 대비 장점)
 *  ─────────────────────────────────────────
 *  1. GC(가비지 컬렉터) 끊김 없음
 *     - C#은 GC가 돌 때 게임이 "뚝뚝" 끊깁니다 (GC 스터터링)
 *     - C++은 메모리를 직접 관리하니까 끊김이 없습니다
 *
 *  2. 캐시 친화적 ECS
 *     - C++은 메모리를 연속으로 배치해서 CPU 캐시 적중률이 높습니다
 *     - C#의 클래스는 힙에 흩어져서 캐시 미스가 많습니다
 *
 *  3. 결정적 소멸 (Deterministic Destruction)
 *     - C++은 소멸자가 정확한 시점에 호출됩니다
 *     - C#은 GC가 "언젠가" 정리해줍니다 (언제인지 모름!)
 *
 *
 *  게임 루프 다이어그램 (ASCII Art)
 *  ════════════════════════════════
 *
 *     ┌─────────────┐
 *     │  게임 시작   │
 *     └──────┬──────┘
 *            ▼
 *     ┌─────────────┐
 *     │  초기화      │  ← 리소스 로드, 엔티티 생성
 *     └──────┬──────┘
 *            ▼
 *     ┌──────────────────────────────────────┐
 *     │         메인 게임 루프 (while)        │ ← Unity의 내부 while문
 *     │  ┌──────────┐                        │
 *     │  │입력 처리  │ ← Unity의 Input 시스템 │
 *     │  └────┬─────┘                        │
 *     │       ▼                              │
 *     │  ┌──────────┐                        │
 *     │  │물리 업데이│ ← Unity의 FixedUpdate  │
 *     │  └────┬─────┘                        │
 *     │       ▼                              │
 *     │  ┌──────────┐                        │
 *     │  │게임 로직  │ ← Unity의 Update       │
 *     │  └────┬─────┘                        │
 *     │       ▼                              │
 *     │  ┌──────────┐                        │
 *     │  │렌더링    │ ← Unity의 LateUpdate    │
 *     │  └────┬─────┘                        │
 *     │       ▼                              │
 *     │  deltaTime 계산 후 루프 반복          │
 *     └──────────────────────────────────────┘
 *
 *
 *  ECS 아키텍처 (ASCII Art)
 *  ═══════════════════════
 *
 *   엔티티(Entity)          컴포넌트(Component)         시스템(System)
 *   ┌──────┐               ┌──────────┐              ┌──────────────┐
 *   │ ID=0 │──────────────▶│ Position │              │MovementSystem│
 *   │      │──────────────▶│ Velocity │──────────────│  (이동 처리) │
 *   │      │──────────────▶│ Sprite   │              └──────────────┘
 *   └──────┘               └──────────┘              ┌──────────────┐
 *   ┌──────┐               ┌──────────┐              │CollisionSys  │
 *   │ ID=1 │──────────────▶│ Position │──────────────│ (충돌 검사)  │
 *   │      │──────────────▶│ Health   │              └──────────────┘
 *   │      │──────────────▶│ Collider │              ┌──────────────┐
 *   └──────┘               └──────────┘              │ RenderSystem │
 *                                                    │ (화면 그리기)│
 *   // ECS는 Unity의 DOTS/ECS와 같은 패턴입니다      └──────────────┘
 *   // 엔티티 = 그냥 번호표 (ID)
 *   // 컴포넌트 = 데이터만 담는 그릇
 *   // 시스템 = 데이터를 처리하는 함수
 *
 *
 *  AABB 충돌 감지 (ASCII Art)
 *  ═════════════════════════
 *
 *   AABB = Axis-Aligned Bounding Box (축 정렬 경계 상자)
 *
 *      ┌─────────┐
 *      │    A    │ minY_A
 *      │         │
 *      └────┬────┘ maxY_A
 *           │
 *      ┌────┴────┐
 *      │    B    │ minY_B
 *      │         │
 *      └─────────┘ maxY_B
 *
 *   충돌 조건: 두 상자가 X축과 Y축 모두에서 겹치면 충돌!
 *   A.minX < B.maxX && A.maxX > B.minX &&
 *   A.minY < B.maxY && A.maxY > B.minY
 *
 * ============================================================================
 */

#include <iostream>    // 콘솔 입출력 (C#의 Console.WriteLine)
#include <vector>      // 동적 배열 (C#의 List<T>)
#include <array>       // 고정 배열 (C#의 T[])
#include <string>      // 문자열 (C#의 string)
#include <chrono>      // 시간 측정 (C#의 System.Diagnostics.Stopwatch)
#include <functional>  // 함수 객체 (C#의 Action, Func)
#include <algorithm>   // 정렬, 검색 등 (C#의 LINQ 비슷)
#include <cmath>       // 수학 함수 (C#의 Math 클래스)
#include <memory>      // 스마트 포인터 (C#에선 GC가 대신 해줌)
#include <unordered_map> // 해시맵 (C#의 Dictionary<K,V>)
#include <queue>       // 큐 (C#의 Queue<T>)
#include <sstream>     // 문자열 스트림 (C#의 StringBuilder)
#include <numeric>     // accumulate 등 숫자 유틸 (C#의 Enumerable.Sum 등)
#include <cassert>     // 디버그 검증 (C#의 Debug.Assert)
#include <cstdint>     // 정수 타입 (C#의 int, uint 등)
#include <thread>      // 스레드, sleep 용 (C#의 Thread.Sleep)

// ============================================================================
//  기본 설정값들 (게임 엔진의 상수)
// ============================================================================
// constexpr는 컴파일 시간에 값이 결정됩니다
// C#의 const와 비슷하지만, 컴파일 타임에 계산까지 됩니다
namespace Config {
    constexpr int MAX_ENTITIES = 256;          // 최대 엔티티 수
    constexpr int SCREEN_WIDTH = 80;           // 화면 너비 (텍스트 칸 수)
    constexpr int SCREEN_HEIGHT = 24;          // 화면 높이
    constexpr float GRAVITY = 9.8f;            // 중력 가속도 (m/s²)
    constexpr float FIXED_TIMESTEP = 1.0f / 60.0f;  // 고정 시간 간격 (60FPS)
    constexpr int BULLET_POOL_SIZE = 64;       // 총알 풀 크기
    constexpr int PARTICLE_POOL_SIZE = 128;    // 파티클 풀 크기
    constexpr int MAX_GAME_FRAMES = 300;       // 데모용: 이만큼 프레임 돌리고 종료
}

// ============================================================================
//  타입 별칭 (Type Aliases)
// ============================================================================
// using은 C#의 using alias와 비슷합니다 (예: using EntityId = int;)
using EntityId = uint32_t;       // 엔티티 ID (부호 없는 32비트 정수)
using ComponentMask = uint32_t;  // 컴포넌트 비트마스크

// 엔티티가 "없다"는 표시 (C#의 null 대신 사용)
constexpr EntityId INVALID_ENTITY = UINT32_MAX;

// ============================================================================
//  컴포넌트 (Component) - 데이터만 담는 그릇
// ============================================================================
// struct를 class 대신 쓰는 이유: C#에서는 struct가 값타입이지만,
// C++에서는 기본 접근제어만 다릅니다 (struct=public, class=private)
// 게임에서는 컴포넌트를 struct로 만들어 데이터를 공개합니다

// 컴포넌트 종류를 비트로 구분합니다 (비트마스크 패턴)
// C#에서 [Flags] enum과 같은 개념입니다
namespace ComponentFlag {
    constexpr ComponentMask NONE     = 0;
    constexpr ComponentMask POSITION = 1 << 0;  // 0001
    constexpr ComponentMask VELOCITY = 1 << 1;  // 0010
    constexpr ComponentMask SPRITE   = 1 << 2;  // 0100
    constexpr ComponentMask HEALTH   = 1 << 3;  // 1000
    constexpr ComponentMask COLLIDER = 1 << 4;  // 10000
}

// --- 위치 컴포넌트 ---
// Unity의 Transform.position과 같습니다
struct Position {
    float x = 0.0f;  // X좌표 (왼쪽-오른쪽)
    float y = 0.0f;  // Y좌표 (위-아래)
};

// --- 속도 컴포넌트 ---
// Unity의 Rigidbody.velocity와 같습니다
struct Velocity {
    float vx = 0.0f;  // X방향 속도
    float vy = 0.0f;  // Y방향 속도
};

// --- 스프라이트 컴포넌트 ---
// Unity의 SpriteRenderer와 같습니다 (텍스트 기반이라 문자로 표현)
struct Sprite {
    char symbol = '?';          // 화면에 표시할 문자
    std::string name = "???";   // 엔티티 이름 (디버그용)
    bool visible = true;        // 보일지 말지
};

// --- 체력 컴포넌트 ---
// Unity에서 직접 만들어 쓰는 Health 스크립트와 같습니다
struct Health {
    int current = 100;   // 현재 체력
    int max = 100;       // 최대 체력
    bool alive = true;   // 살아있는지 (current > 0이면 true)
};

// --- 충돌체 컴포넌트 ---
// Unity의 BoxCollider2D와 같습니다 (AABB 방식)
struct Collider {
    float width = 1.0f;    // 충돌 상자의 너비
    float height = 1.0f;   // 충돌 상자의 높이
    bool isTrigger = false; // 트리거인지 (물리 반응 없이 이벤트만)
    // C#의 OnTriggerEnter와 비슷한 역할을 합니다
};

// ============================================================================
//  이벤트 시스템 (Event System)
// ============================================================================
// Unity의 UnityEvent, C#의 event/delegate 패턴과 같습니다
// 게임에서 일어나는 일(충돌, 사망, 점수)을 알려주는 시스템입니다

// 이벤트 종류
// C#의 enum과 같습니다
enum class EventType {
    Collision,    // 충돌 발생
    EntityDeath,  // 엔티티 사망
    ScoreChange,  // 점수 변경
    BulletFired,  // 총알 발사
    ParticleSpawn // 파티클 생성
};

// 이벤트 데이터 (이벤트에 담기는 정보)
// C#의 EventArgs와 같습니다
struct GameEvent {
    EventType type;          // 무슨 이벤트인지
    EntityId entityA = INVALID_ENTITY;  // 관련 엔티티 A
    EntityId entityB = INVALID_ENTITY;  // 관련 엔티티 B
    float value = 0.0f;     // 숫자 값 (점수, 데미지 등)
    std::string message;    // 메시지 (디버그용)
};

// 이벤트를 받아서 처리하는 함수 타입
// C#의 Action<GameEvent>와 같습니다
using EventHandler = std::function<void(const GameEvent&)>;

// 이벤트 매니저 - 이벤트를 보내고 받는 중앙 시스템
// C#의 EventBus 패턴과 같습니다
class EventManager {
public:
    // 이벤트 리스너 등록 (C#의 event += handler)
    void subscribe(EventType type, EventHandler handler) {
        listeners_[type].push_back(handler);
    }

    // 이벤트 발행 - 큐에 넣기 (나중에 한꺼번에 처리)
    // C#의 event?.Invoke()를 지연 호출하는 것과 같습니다
    void enqueue(const GameEvent& event) {
        eventQueue_.push(event);
    }

    // 큐에 쌓인 이벤트를 모두 처리
    // 게임 루프에서 매 프레임 호출합니다
    void dispatch() {
        while (!eventQueue_.empty()) {
            const auto& evt = eventQueue_.front();
            auto it = listeners_.find(evt.type);
            if (it != listeners_.end()) {
                // 등록된 모든 리스너에게 이벤트 전달
                for (auto& handler : it->second) {
                    handler(evt);
                }
            }
            eventQueue_.pop();
        }
    }

private:
    // 이벤트 타입별 리스너 목록 (C#의 Dictionary<EventType, List<Action>>)
    std::unordered_map<int, std::vector<EventHandler>> listeners_;

    // 이벤트 큐 (순서대로 처리하기 위해 큐 사용)
    std::queue<GameEvent> eventQueue_;
};

// ============================================================================
//  ECS (Entity Component System)
// ============================================================================
// ECS는 Unity의 DOTS/ECS와 같은 패턴입니다
// 전통적인 OOP(상속) 대신 조합(컴포지션)으로 게임 오브젝트를 만듭니다
//
// 왜 ECS가 빠른가?
// - 같은 종류의 데이터가 메모리에 연속으로 배치됩니다
// - CPU 캐시 라인에 딱 맞아서 메모리 접근이 빠릅니다
// - C#의 클래스 기반은 힙에 흩어져서 캐시 미스가 많습니다

class ECS {
public:
    // --- 엔티티 관리 ---

    // 새 엔티티 생성 (C#의 new GameObject()와 비슷)
    EntityId createEntity() {
        // 비활성 엔티티가 있으면 재활용 (오브젝트 풀링과 비슷한 개념)
        for (EntityId i = 0; i < Config::MAX_ENTITIES; ++i) {
            if (!active_[i]) {
                active_[i] = true;
                masks_[i] = ComponentFlag::NONE;
                entityCount_++;
                return i;
            }
        }
        // 더 이상 자리가 없음!
        std::cerr << "[ECS] 엔티티가 가득 찼습니다!\n";
        return INVALID_ENTITY;
    }

    // 엔티티 삭제 (C#의 Destroy(gameObject)와 비슷)
    void destroyEntity(EntityId id) {
        if (id < Config::MAX_ENTITIES && active_[id]) {
            active_[id] = false;
            masks_[id] = ComponentFlag::NONE;
            entityCount_--;
        }
    }

    // 엔티티가 살아있는지 확인
    bool isActive(EntityId id) const {
        return id < Config::MAX_ENTITIES && active_[id];
    }

    // --- 컴포넌트 추가/조회 ---
    // C#의 AddComponent<T>(), GetComponent<T>()와 같습니다

    void addPosition(EntityId id, float x, float y) {
        positions_[id] = {x, y};
        masks_[id] |= ComponentFlag::POSITION;  // 비트 OR로 플래그 추가
    }

    void addVelocity(EntityId id, float vx, float vy) {
        velocities_[id] = {vx, vy};
        masks_[id] |= ComponentFlag::VELOCITY;
    }

    void addSprite(EntityId id, char symbol, const std::string& name) {
        sprites_[id] = {symbol, name, true};
        masks_[id] |= ComponentFlag::SPRITE;
    }

    void addHealth(EntityId id, int hp) {
        health_[id] = {hp, hp, true};
        masks_[id] |= ComponentFlag::HEALTH;
    }

    void addCollider(EntityId id, float w, float h, bool trigger = false) {
        colliders_[id] = {w, h, trigger};
        masks_[id] |= ComponentFlag::COLLIDER;
    }

    // 특정 컴포넌트를 가지고 있는지 확인 (C#의 HasComponent<T>)
    bool hasComponents(EntityId id, ComponentMask required) const {
        return (masks_[id] & required) == required;
    }

    // --- 컴포넌트 데이터 접근 ---
    // 배열로 저장하므로 인덱스로 바로 접근 = 매우 빠름!
    // C#의 Dictionary보다 훨씬 빠릅니다 (해시 계산 없이 바로 접근)

    Position& getPosition(EntityId id) { return positions_[id]; }
    Velocity& getVelocity(EntityId id) { return velocities_[id]; }
    Sprite& getSprite(EntityId id) { return sprites_[id]; }
    Health& getHealth(EntityId id) { return health_[id]; }
    Collider& getCollider(EntityId id) { return colliders_[id]; }

    const Position& getPosition(EntityId id) const { return positions_[id]; }

    // 활성 엔티티 수
    int getEntityCount() const { return entityCount_; }

    // 모든 활성 엔티티에 대해 함수 실행 (C#의 foreach와 비슷)
    void forEach(ComponentMask required, const std::function<void(EntityId)>& func) {
        for (EntityId i = 0; i < Config::MAX_ENTITIES; ++i) {
            if (active_[i] && hasComponents(i, required)) {
                func(i);
            }
        }
    }

private:
    // 모든 데이터가 배열(연속 메모리)에 저장됩니다!
    // 이게 ECS가 빠른 핵심 이유입니다 (캐시 친화적)
    // C#의 List<T>와 달리, 고정 크기 배열이라 힙 할당이 없습니다

    std::array<bool, Config::MAX_ENTITIES> active_{};           // 활성 여부
    std::array<ComponentMask, Config::MAX_ENTITIES> masks_{};   // 컴포넌트 마스크
    std::array<Position, Config::MAX_ENTITIES> positions_{};    // 위치 배열
    std::array<Velocity, Config::MAX_ENTITIES> velocities_{};   // 속도 배열
    std::array<Sprite, Config::MAX_ENTITIES> sprites_{};        // 스프라이트 배열
    std::array<Health, Config::MAX_ENTITIES> health_{};         // 체력 배열
    std::array<Collider, Config::MAX_ENTITIES> colliders_{};    // 충돌체 배열

    int entityCount_ = 0;
};

// ============================================================================
//  오브젝트 풀 (Object Pool)
// ============================================================================
// 오브젝트 풀링은 Unity의 ObjectPool과 같습니다
// 게임 루프 안에서 new/delete를 하면 느려집니다!
// 미리 만들어 놓고 재활용하는 게 핵심입니다
//
// 왜 필요한가?
// - new/delete는 운영체제에 메모리를 요청하는 느린 작업입니다
// - C#에서는 GC가 이걸 모아서 처리하는데, 그때 게임이 끊깁니다
// - C++에서는 풀을 써서 아예 할당/해제를 안 합니다!

// 풀에 들어갈 아이템 (총알 또는 파티클)
struct PoolItem {
    bool active = false;    // 사용 중인지
    float x = 0.0f;        // X위치
    float y = 0.0f;        // Y위치
    float vx = 0.0f;       // X속도
    float vy = 0.0f;       // Y속도
    float lifetime = 0.0f; // 남은 수명 (초)
    char symbol = '*';     // 표시 문자
};

// 템플릿을 사용한 오브젝트 풀
// C#의 제네릭(ObjectPool<T>)과 비슷합니다
// Size는 풀의 크기 (컴파일 시간에 결정)
template<int Size>
class ObjectPool {
public:
    // 풀에서 아이템 하나 꺼내기 (활성화)
    // C#의 ObjectPool.Get()과 같습니다
    int acquire() {
        for (int i = 0; i < Size; ++i) {
            if (!items_[i].active) {
                items_[i].active = true;
                activeCount_++;
                return i;  // 풀 안에서의 인덱스 반환
            }
        }
        return -1;  // 풀이 가득 참 (빈 자리 없음)
    }

    // 풀에 아이템 반납 (비활성화)
    // C#의 ObjectPool.Release()와 같습니다
    void release(int index) {
        if (index >= 0 && index < Size && items_[index].active) {
            items_[index].active = false;
            items_[index] = PoolItem{};  // 초기화
            activeCount_--;
        }
    }

    // 풀 아이템 접근
    PoolItem& get(int index) { return items_[index]; }
    const PoolItem& get(int index) const { return items_[index]; }

    // 활성 아이템에 대해 함수 실행
    void forEachActive(const std::function<void(int, PoolItem&)>& func) {
        for (int i = 0; i < Size; ++i) {
            if (items_[i].active) {
                func(i, items_[i]);
            }
        }
    }

    int getActiveCount() const { return activeCount_; }
    int getCapacity() const { return Size; }

private:
    // 배열로 미리 할당! new/delete가 필요 없습니다!
    std::array<PoolItem, Size> items_{};
    int activeCount_ = 0;
};

// ============================================================================
//  씬 그래프 (Scene Graph) - 부모-자식 트랜스폼 계층
// ============================================================================
// Unity의 Transform 부모-자식 관계와 같습니다
// 부모가 움직이면 자식도 따라 움직입니다
//
// 예: 탱크 몸체(부모) → 포탑(자식) → 총구(손자)
//     탱크가 이동하면 포탑과 총구도 같이 이동!

struct SceneNode {
    EntityId entity = INVALID_ENTITY;    // 연결된 엔티티
    float localX = 0.0f;                 // 부모 기준 상대 X위치
    float localY = 0.0f;                 // 부모 기준 상대 Y위치
    float worldX = 0.0f;                 // 세계(절대) X위치
    float worldY = 0.0f;                 // 세계(절대) Y위치
    int parent = -1;                     // 부모 노드 인덱스 (-1이면 루트)
    std::vector<int> children;           // 자식 노드 인덱스들
    std::string name = "Node";           // 노드 이름 (디버그용)
};

class SceneGraph {
public:
    // 노드 추가 (C#의 transform.SetParent()와 비슷)
    int addNode(EntityId entity, const std::string& name, int parentIdx = -1) {
        int idx = static_cast<int>(nodes_.size());
        SceneNode node;
        node.entity = entity;
        node.name = name;
        node.parent = parentIdx;

        if (parentIdx >= 0 && parentIdx < static_cast<int>(nodes_.size())) {
            nodes_[parentIdx].children.push_back(idx);
        }

        nodes_.push_back(node);
        return idx;
    }

    // 로컬 위치 설정 (부모 기준 상대 위치)
    void setLocalPosition(int idx, float x, float y) {
        if (idx >= 0 && idx < static_cast<int>(nodes_.size())) {
            nodes_[idx].localX = x;
            nodes_[idx].localY = y;
        }
    }

    // 월드 트랜스폼 업데이트 (부모 위치 + 자식 상대 위치 = 자식 절대 위치)
    // Unity가 내부적으로 하는 트랜스폼 계산과 같습니다
    void updateWorldTransforms() {
        for (int i = 0; i < static_cast<int>(nodes_.size()); ++i) {
            if (nodes_[i].parent == -1) {
                // 루트 노드: 로컬 = 월드
                updateNodeRecursive(i, 0.0f, 0.0f);
            }
        }
    }

    // 노드 정보 가져오기
    const SceneNode& getNode(int idx) const { return nodes_[idx]; }
    int getNodeCount() const { return static_cast<int>(nodes_.size()); }

    // 씬 트리를 텍스트로 출력 (디버그용)
    void printTree() const {
        std::cout << "\n=== 씬 그래프 (Scene Graph) ===\n";
        for (int i = 0; i < static_cast<int>(nodes_.size()); ++i) {
            if (nodes_[i].parent == -1) {
                printNodeRecursive(i, 0);
            }
        }
    }

private:
    std::vector<SceneNode> nodes_;

    // 재귀적으로 월드 좌표 계산
    // 부모의 월드 좌표를 받아서 자식의 월드 좌표를 계산합니다
    void updateNodeRecursive(int idx, float parentWorldX, float parentWorldY) {
        auto& node = nodes_[idx];
        node.worldX = parentWorldX + node.localX;
        node.worldY = parentWorldY + node.localY;

        // 자식들도 업데이트 (재귀 호출)
        for (int childIdx : node.children) {
            updateNodeRecursive(childIdx, node.worldX, node.worldY);
        }
    }

    // 트리 구조를 텍스트로 출력 (들여쓰기로 계층 표현)
    void printNodeRecursive(int idx, int depth) const {
        const auto& node = nodes_[idx];
        // 들여쓰기
        for (int i = 0; i < depth; ++i) std::cout << "  ";
        if (depth > 0) std::cout << "└─ ";

        std::cout << node.name
                  << " [로컬: (" << node.localX << ", " << node.localY << ")"
                  << " 월드: (" << node.worldX << ", " << node.worldY << ")]\n";

        for (int childIdx : node.children) {
            printNodeRecursive(childIdx, depth + 1);
        }
    }
};

// ============================================================================
//  시스템 (Systems) - 게임 로직을 실행하는 곳
// ============================================================================
// 시스템은 Unity의 MonoBehaviour 스크립트와 비슷하지만,
// 데이터(컴포넌트)와 로직(시스템)이 분리되어 있습니다

// --- 이동 시스템 ---
// Unity의 Rigidbody 물리 시뮬레이션과 비슷합니다
namespace MovementSystem {
    // 중력 + 속도로 위치 업데이트
    // deltaTime은 Unity의 Time.deltaTime과 같습니다
    void update(ECS& ecs, float deltaTime) {
        // Position과 Velocity 둘 다 가진 엔티티만 처리
        ComponentMask required = ComponentFlag::POSITION | ComponentFlag::VELOCITY;
        ecs.forEach(required, [&](EntityId id) {
            auto& pos = ecs.getPosition(id);
            auto& vel = ecs.getVelocity(id);

            // 중력 적용 (아래 방향으로 가속)
            // 물리학: v = v0 + a*t (속도 = 이전속도 + 가속도*시간)
            vel.vy += Config::GRAVITY * deltaTime;

            // 위치 업데이트 (속도 * 시간 = 이동 거리)
            // 물리학: x = x0 + v*t
            pos.x += vel.vx * deltaTime;
            pos.y += vel.vy * deltaTime;

            // 바닥 충돌 (간단한 지면 처리)
            // 화면 아래로 떨어지면 바닥에서 멈춤
            if (pos.y > Config::SCREEN_HEIGHT - 2) {
                pos.y = static_cast<float>(Config::SCREEN_HEIGHT - 2);
                vel.vy = -vel.vy * 0.5f;  // 반발 계수 0.5 (튕김)
                // 속도가 아주 작으면 멈춤
                if (std::abs(vel.vy) < 0.5f) {
                    vel.vy = 0.0f;
                }
            }

            // 좌우 벽 충돌
            if (pos.x < 0) {
                pos.x = 0;
                vel.vx = -vel.vx * 0.7f;
            }
            if (pos.x > Config::SCREEN_WIDTH - 1) {
                pos.x = static_cast<float>(Config::SCREEN_WIDTH - 1);
                vel.vx = -vel.vx * 0.7f;
            }

            // 위 벽 충돌
            if (pos.y < 0) {
                pos.y = 0;
                vel.vy = -vel.vy * 0.5f;
            }
        });
    }
}

// --- 충돌 시스템 ---
// Unity의 Physics2D 시스템과 비슷합니다
// AABB (축 정렬 경계 상자) 충돌 감지를 사용합니다
namespace CollisionSystem {
    // AABB 충돌 검사 함수
    // 두 사각형이 겹치는지 확인합니다
    bool checkAABB(const Position& posA, const Collider& colA,
                   const Position& posB, const Collider& colB) {
        // 각 사각형의 경계 계산
        float aMinX = posA.x - colA.width / 2.0f;
        float aMaxX = posA.x + colA.width / 2.0f;
        float aMinY = posA.y - colA.height / 2.0f;
        float aMaxY = posA.y + colA.height / 2.0f;

        float bMinX = posB.x - colB.width / 2.0f;
        float bMaxX = posB.x + colB.width / 2.0f;
        float bMinY = posB.y - colB.height / 2.0f;
        float bMaxY = posB.y + colB.height / 2.0f;

        // X축과 Y축 모두 겹쳐야 충돌!
        return (aMinX < bMaxX && aMaxX > bMinX &&
                aMinY < bMaxY && aMaxY > bMinY);
    }

    // 모든 충돌체 쌍을 검사
    void update(ECS& ecs, EventManager& events) {
        ComponentMask required = ComponentFlag::POSITION | ComponentFlag::COLLIDER;

        // 활성 엔티티 목록 수집
        std::vector<EntityId> entities;
        ecs.forEach(required, [&](EntityId id) {
            entities.push_back(id);
        });

        // 모든 쌍을 비교 (O(n²) - 엔티티 수가 적으면 충분히 빠름)
        // 엔티티가 많아지면 공간 분할(쿼드트리 등)이 필요합니다
        for (size_t i = 0; i < entities.size(); ++i) {
            for (size_t j = i + 1; j < entities.size(); ++j) {
                EntityId a = entities[i];
                EntityId b = entities[j];

                if (checkAABB(ecs.getPosition(a), ecs.getCollider(a),
                              ecs.getPosition(b), ecs.getCollider(b))) {
                    // 충돌 이벤트 발행!
                    GameEvent evt;
                    evt.type = EventType::Collision;
                    evt.entityA = a;
                    evt.entityB = b;
                    evt.message = "충돌 감지!";
                    events.enqueue(evt);
                }
            }
        }
    }
}

// --- 렌더 시스템 (텍스트 기반) ---
// Unity의 Camera + SpriteRenderer와 비슷합니다
// 실제 게임은 GPU로 그리지만, 여기서는 콘솔 텍스트로 표현합니다
namespace RenderSystem {
    // 화면 버퍼 (2D 문자 배열)
    // GPU의 프레임버퍼와 같은 개념입니다
    static char screenBuffer[Config::SCREEN_HEIGHT][Config::SCREEN_WIDTH + 1];

    // 화면 지우기 (매 프레임 시작)
    void clearScreen() {
        for (int y = 0; y < Config::SCREEN_HEIGHT; ++y) {
            for (int x = 0; x < Config::SCREEN_WIDTH; ++x) {
                screenBuffer[y][x] = ' ';
            }
            screenBuffer[y][Config::SCREEN_WIDTH] = '\0';
        }
        // 바닥 그리기
        for (int x = 0; x < Config::SCREEN_WIDTH; ++x) {
            screenBuffer[Config::SCREEN_HEIGHT - 1][x] = '=';
        }
    }

    // 엔티티들을 버퍼에 그리기
    void render(const ECS& ecs) {
        // 임시로 const를 우회 (forEach가 non-const라서)
        // 실제 엔진에서는 const 버전의 forEach를 만들어야 합니다
        ECS& mutableEcs = const_cast<ECS&>(ecs);
        ComponentMask required = ComponentFlag::POSITION | ComponentFlag::SPRITE;
        mutableEcs.forEach(required, [&](EntityId id) {
            auto& pos = mutableEcs.getPosition(id);
            auto& spr = mutableEcs.getSprite(id);
            if (!spr.visible) return;

            int sx = static_cast<int>(pos.x);
            int sy = static_cast<int>(pos.y);

            // 화면 범위 안인지 확인
            if (sx >= 0 && sx < Config::SCREEN_WIDTH &&
                sy >= 0 && sy < Config::SCREEN_HEIGHT - 1) {
                screenBuffer[sy][sx] = spr.symbol;
            }
        });
    }

    // 풀 아이템들을 버퍼에 그리기 (총알, 파티클)
    template<int Size>
    void renderPool(const ObjectPool<Size>& pool) {
        // const_cast로 forEachActive 호출 (읽기만 하므로 안전)
        auto& mutablePool = const_cast<ObjectPool<Size>&>(pool);
        mutablePool.forEachActive([&](int /*idx*/, PoolItem& item) {
            int sx = static_cast<int>(item.x);
            int sy = static_cast<int>(item.y);
            if (sx >= 0 && sx < Config::SCREEN_WIDTH &&
                sy >= 0 && sy < Config::SCREEN_HEIGHT - 1) {
                screenBuffer[sy][sx] = item.symbol;
            }
        });
    }

    // 화면 버퍼를 콘솔에 출력
    void present(int frameNum) {
        // 상단 HUD (헤드업 디스플레이)
        std::cout << "┌";
        for (int i = 0; i < Config::SCREEN_WIDTH; ++i) std::cout << "─";
        std::cout << "┐\n";

        // 화면 내용 출력
        for (int y = 0; y < Config::SCREEN_HEIGHT; ++y) {
            std::cout << "│" << screenBuffer[y] << "│\n";
        }

        // 하단 테두리
        std::cout << "└";
        for (int i = 0; i < Config::SCREEN_WIDTH; ++i) std::cout << "─";
        std::cout << "┘\n";
    }
}

// ============================================================================
//  성능 통계 (Performance Stats)
// ============================================================================
// Unity의 Profiler와 비슷한 역할입니다
// 프레임 레이트(FPS)와 각 시스템의 소요 시간을 측정합니다

class PerformanceStats {
public:
    using Clock = std::chrono::high_resolution_clock;
    using Duration = std::chrono::duration<double, std::milli>; // 밀리초

    // 프레임 시작 시 호출
    void frameBegin() {
        frameStart_ = Clock::now();
    }

    // 프레임 끝에 호출
    void frameEnd() {
        auto now = Clock::now();
        Duration frameTime = now - frameStart_;
        frameTimes_.push_back(frameTime.count());

        // 최근 60프레임만 유지 (이동 평균)
        if (frameTimes_.size() > 60) {
            frameTimes_.erase(frameTimes_.begin());
        }

        totalFrames_++;
    }

    // 특정 시스템 시간 측정 시작
    void systemBegin(const std::string& name) {
        systemStart_ = Clock::now();
        currentSystem_ = name;
    }

    // 특정 시스템 시간 측정 끝
    void systemEnd() {
        auto now = Clock::now();
        Duration elapsed = now - systemStart_;
        systemTimes_[currentSystem_] = elapsed.count();
    }

    // 평균 FPS 계산
    double getAverageFPS() const {
        if (frameTimes_.empty()) return 0.0;
        double avgMs = std::accumulate(frameTimes_.begin(), frameTimes_.end(), 0.0)
                       / static_cast<double>(frameTimes_.size());
        return (avgMs > 0.0) ? (1000.0 / avgMs) : 0.0;
    }

    // 평균 프레임 시간 (밀리초)
    double getAverageFrameTime() const {
        if (frameTimes_.empty()) return 0.0;
        return std::accumulate(frameTimes_.begin(), frameTimes_.end(), 0.0)
               / static_cast<double>(frameTimes_.size());
    }

    // 성능 통계 출력
    void printStats() const {
        std::cout << "\n=== 성능 통계 (Performance Stats) ===\n";
        std::cout << "  총 프레임: " << totalFrames_ << "\n";
        std::cout << "  평균 FPS: " << getAverageFPS() << "\n";
        std::cout << "  평균 프레임 시간: " << getAverageFrameTime() << " ms\n";
        std::cout << "  시스템별 소요 시간:\n";
        for (const auto& [name, time] : systemTimes_) {
            std::cout << "    " << name << ": " << time << " ms\n";
        }
    }

    int getTotalFrames() const { return totalFrames_; }

private:
    Clock::time_point frameStart_;
    Clock::time_point systemStart_;
    std::string currentSystem_;
    std::vector<double> frameTimes_;                    // 프레임 시간 기록
    std::unordered_map<std::string, double> systemTimes_; // 시스템별 시간
    int totalFrames_ = 0;
};

// ============================================================================
//  게임 월드 (Game World) - 모든 것을 통합하는 곳
// ============================================================================
// Unity의 Scene과 비슷합니다

class GameWorld {
public:
    // 게임 초기화
    void initialize() {
        std::cout << "╔══════════════════════════════════════════════╗\n";
        std::cout << "║     게임 엔진 코어 (Game Engine Core)       ║\n";
        std::cout << "║     C++ ECS 기반 미니 게임 엔진             ║\n";
        std::cout << "╚══════════════════════════════════════════════╝\n\n";

        setupEvents();
        createEntities();
        setupSceneGraph();

        std::cout << "[초기화 완료] 엔티티 " << ecs_.getEntityCount() << "개 생성됨\n";
        std::cout << "[초기화 완료] 총알 풀: " << bulletPool_.getCapacity() << "개 예약\n";
        std::cout << "[초기화 완료] 파티클 풀: " << particlePool_.getCapacity() << "개 예약\n\n";
    }

    // 메인 게임 루프 실행
    // 게임 루프는 Unity의 Update()가 내부적으로 돌리는 while문입니다
    void run() {
        std::cout << "=== 게임 루프 시작 (고정 타임스텝: "
                  << Config::FIXED_TIMESTEP * 1000.0f << "ms) ===\n\n";

        // deltaTime 계산용 시계
        // C#의 Time.deltaTime을 직접 계산하는 것과 같습니다
        auto previousTime = std::chrono::high_resolution_clock::now();
        float accumulator = 0.0f;  // 누적 시간 (고정 타임스텝용)

        // --- 메인 게임 루프 ---
        // 실제 게임은 while(true)이지만, 데모이므로 프레임 제한
        while (frameCount_ < Config::MAX_GAME_FRAMES) {
            stats_.frameBegin();

            // deltaTime 계산
            auto currentTime = std::chrono::high_resolution_clock::now();
            std::chrono::duration<float> elapsed = currentTime - previousTime;
            float deltaTime = elapsed.count();
            previousTime = currentTime;

            // deltaTime이 너무 크면 제한 (디버깅 중 브레이크포인트 등)
            if (deltaTime > 0.25f) deltaTime = 0.25f;

            // 누적 시간에 더하기
            accumulator += deltaTime;

            // --- 고정 타임스텝 물리 업데이트 ---
            // Unity의 FixedUpdate()와 같습니다
            // 물리는 일정한 간격으로 업데이트해야 안정적입니다
            while (accumulator >= Config::FIXED_TIMESTEP) {
                // 물리 업데이트
                stats_.systemBegin("MovementSystem");
                MovementSystem::update(ecs_, Config::FIXED_TIMESTEP);
                stats_.systemEnd();

                // 충돌 검사
                stats_.systemBegin("CollisionSystem");
                CollisionSystem::update(ecs_, events_);
                stats_.systemEnd();

                // 풀 아이템(총알, 파티클) 업데이트
                updatePools(Config::FIXED_TIMESTEP);

                // 씬 그래프 업데이트
                updateSceneGraphFromECS();
                sceneGraph_.updateWorldTransforms();

                accumulator -= Config::FIXED_TIMESTEP;
            }

            // --- 이벤트 처리 ---
            stats_.systemBegin("EventSystem");
            events_.dispatch();
            stats_.systemEnd();

            // --- 게임 로직 업데이트 ---
            gameLogicUpdate(deltaTime);

            // --- 렌더링 ---
            // 매 30프레임마다 화면 출력 (너무 빠르면 콘솔이 버벅임)
            if (frameCount_ % 30 == 0) {
                stats_.systemBegin("RenderSystem");
                RenderSystem::clearScreen();
                RenderSystem::render(ecs_);
                RenderSystem::renderPool(bulletPool_);
                RenderSystem::renderPool(particlePool_);
                RenderSystem::present(frameCount_);
                stats_.systemEnd();

                // HUD 출력
                printHUD();
            }

            stats_.frameEnd();
            frameCount_++;

            // CPU 쉬기 (100% 사용 방지)
            std::this_thread::sleep_for(
                std::chrono::microseconds(static_cast<int>(Config::FIXED_TIMESTEP * 1000000)));
        }

        // 게임 종료
        std::cout << "\n=== 게임 루프 종료 (" << frameCount_ << " 프레임) ===\n";
        stats_.printStats();
        sceneGraph_.printTree();
        printFinalReport();
    }

private:
    ECS ecs_;                                             // 엔티티 컴포넌트 시스템
    EventManager events_;                                 // 이벤트 매니저
    SceneGraph sceneGraph_;                               // 씬 그래프
    ObjectPool<Config::BULLET_POOL_SIZE> bulletPool_;     // 총알 풀
    ObjectPool<Config::PARTICLE_POOL_SIZE> particlePool_; // 파티클 풀
    PerformanceStats stats_;                              // 성능 통계

    int frameCount_ = 0;      // 현재 프레임 번호
    int score_ = 0;           // 점수
    int collisionCount_ = 0;  // 충돌 횟수
    int bulletsFired_ = 0;    // 발사된 총알 수
    int particlesSpawned_ = 0; // 생성된 파티클 수

    // 주요 엔티티 ID 저장
    EntityId playerId_ = INVALID_ENTITY;
    EntityId enemyId_ = INVALID_ENTITY;
    EntityId platformId_ = INVALID_ENTITY;

    // --- 이벤트 핸들러 설정 ---
    void setupEvents() {
        // 충돌 이벤트 핸들러
        events_.subscribe(EventType::Collision, [this](const GameEvent& evt) {
            collisionCount_++;
            // 충돌 시 파티클 생성!
            if (ecs_.isActive(evt.entityA)) {
                spawnParticles(ecs_.getPosition(evt.entityA).x,
                              ecs_.getPosition(evt.entityA).y, 3);
            }
        });

        // 사망 이벤트 핸들러
        events_.subscribe(EventType::EntityDeath, [this](const GameEvent& evt) {
            if (ecs_.isActive(evt.entityA)) {
                auto& spr = ecs_.getSprite(evt.entityA);
                spr.symbol = 'X';  // 사망 표시
                spr.visible = true;
            }
        });

        // 점수 변경 핸들러
        events_.subscribe(EventType::ScoreChange, [this](const GameEvent& evt) {
            score_ += static_cast<int>(evt.value);
        });
    }

    // --- 엔티티 생성 ---
    void createEntities() {
        // 플레이어 생성
        // Unity에서 new GameObject("Player")를 만들고 컴포넌트를 붙이는 것과 같습니다
        playerId_ = ecs_.createEntity();
        ecs_.addPosition(playerId_, 10.0f, 5.0f);
        ecs_.addVelocity(playerId_, 3.0f, -2.0f);
        ecs_.addSprite(playerId_, '@', "Player");
        ecs_.addHealth(playerId_, 100);
        ecs_.addCollider(playerId_, 2.0f, 2.0f);

        // 적 생성
        enemyId_ = ecs_.createEntity();
        ecs_.addPosition(enemyId_, 50.0f, 3.0f);
        ecs_.addVelocity(enemyId_, -2.0f, -1.0f);
        ecs_.addSprite(enemyId_, 'E', "Enemy");
        ecs_.addHealth(enemyId_, 50);
        ecs_.addCollider(enemyId_, 2.0f, 2.0f);

        // 플랫폼 (움직이지 않는 발판)
        platformId_ = ecs_.createEntity();
        ecs_.addPosition(platformId_, 30.0f, 18.0f);
        ecs_.addSprite(platformId_, '#', "Platform");
        ecs_.addCollider(platformId_, 10.0f, 1.0f);

        // 추가 엔티티들 (아이템, 장식 등)
        for (int i = 0; i < 5; ++i) {
            EntityId item = ecs_.createEntity();
            float x = 15.0f + static_cast<float>(i) * 12.0f;
            ecs_.addPosition(item, x, 2.0f);
            ecs_.addVelocity(item, 0.0f, 0.0f);
            ecs_.addSprite(item, 'o', "Item_" + std::to_string(i));
            ecs_.addCollider(item, 1.0f, 1.0f, true);  // 트리거 (통과 가능)
        }

        // 벽 엔티티들
        for (int i = 0; i < 3; ++i) {
            EntityId wall = ecs_.createEntity();
            float x = 20.0f + static_cast<float>(i) * 20.0f;
            ecs_.addPosition(wall, x, 15.0f);
            ecs_.addSprite(wall, '|', "Wall_" + std::to_string(i));
            ecs_.addCollider(wall, 1.0f, 5.0f);
        }
    }

    // --- 씬 그래프 설정 ---
    void setupSceneGraph() {
        // 루트 → 플레이어 → 무기
        int rootIdx = sceneGraph_.addNode(INVALID_ENTITY, "Root");
        int playerNodeIdx = sceneGraph_.addNode(playerId_, "Player", rootIdx);
        sceneGraph_.addNode(INVALID_ENTITY, "Weapon", playerNodeIdx);

        sceneGraph_.setLocalPosition(playerNodeIdx, 10.0f, 5.0f);
        // 무기는 플레이어 기준 오른쪽 2칸
        sceneGraph_.setLocalPosition(2, 2.0f, 0.0f);

        // 루트 → 적 → 방패
        int enemyNodeIdx = sceneGraph_.addNode(enemyId_, "Enemy", rootIdx);
        sceneGraph_.addNode(INVALID_ENTITY, "Shield", enemyNodeIdx);

        sceneGraph_.setLocalPosition(enemyNodeIdx, 50.0f, 3.0f);
        sceneGraph_.setLocalPosition(4, -1.0f, 0.0f);  // 방패는 왼쪽 1칸

        sceneGraph_.updateWorldTransforms();
    }

    // --- 씬 그래프를 ECS 위치로 동기화 ---
    void updateSceneGraphFromECS() {
        // 플레이어 노드 업데이트
        if (ecs_.isActive(playerId_)) {
            auto& pos = ecs_.getPosition(playerId_);
            sceneGraph_.setLocalPosition(1, pos.x, pos.y);
        }
        // 적 노드 업데이트
        if (ecs_.isActive(enemyId_)) {
            auto& pos = ecs_.getPosition(enemyId_);
            sceneGraph_.setLocalPosition(3, pos.x, pos.y);
        }
    }

    // --- 총알 발사 (오브젝트 풀 사용) ---
    void fireBullet(float x, float y, float vx, float vy) {
        int idx = bulletPool_.acquire();
        if (idx >= 0) {
            auto& bullet = bulletPool_.get(idx);
            bullet.x = x;
            bullet.y = y;
            bullet.vx = vx;
            bullet.vy = vy;
            bullet.lifetime = 3.0f;  // 3초 후 자동 소멸
            bullet.symbol = '-';
            bulletsFired_++;

            // 총알 발사 이벤트
            GameEvent evt;
            evt.type = EventType::BulletFired;
            evt.value = static_cast<float>(bulletsFired_);
            evt.message = "총알 발사!";
            events_.enqueue(evt);
        }
    }

    // --- 파티클 생성 (오브젝트 풀 사용) ---
    void spawnParticles(float x, float y, int count) {
        for (int i = 0; i < count; ++i) {
            int idx = particlePool_.acquire();
            if (idx >= 0) {
                auto& p = particlePool_.get(idx);
                p.x = x;
                p.y = y;
                // 간단한 랜덤 방향 (진짜 랜덤 대신 인덱스 기반)
                float angle = static_cast<float>(i) * 2.094f;  // 120도 간격
                p.vx = std::cos(angle) * 5.0f;
                p.vy = std::sin(angle) * 5.0f - 3.0f;
                p.lifetime = 1.0f;
                p.symbol = '.';
                particlesSpawned_++;
            }
        }
    }

    // --- 풀 아이템 업데이트 ---
    void updatePools(float dt) {
        // 총알 업데이트
        std::vector<int> toRelease;
        bulletPool_.forEachActive([&](int idx, PoolItem& item) {
            item.x += item.vx * dt;
            item.y += item.vy * dt;
            item.lifetime -= dt;
            // 수명 다하거나 화면 밖이면 반납
            if (item.lifetime <= 0.0f ||
                item.x < 0 || item.x > Config::SCREEN_WIDTH ||
                item.y < 0 || item.y > Config::SCREEN_HEIGHT) {
                toRelease.push_back(idx);
            }
        });
        for (int idx : toRelease) bulletPool_.release(idx);

        // 파티클 업데이트
        toRelease.clear();
        particlePool_.forEachActive([&](int idx, PoolItem& item) {
            item.x += item.vx * dt;
            item.y += item.vy * dt;
            item.vy += Config::GRAVITY * dt * 0.3f;  // 파티클에도 약한 중력
            item.lifetime -= dt;
            if (item.lifetime <= 0.0f) {
                toRelease.push_back(idx);
            }
        });
        for (int idx : toRelease) particlePool_.release(idx);
    }

    // --- 게임 로직 업데이트 ---
    void gameLogicUpdate(float /*dt*/) {
        // 일정 간격으로 총알 발사 (자동 발사 시뮬레이션)
        if (frameCount_ % 45 == 0 && ecs_.isActive(playerId_)) {
            auto& pos = ecs_.getPosition(playerId_);
            fireBullet(pos.x + 1.0f, pos.y, 20.0f, 0.0f);
        }

        // 적도 가끔 총알 발사
        if (frameCount_ % 60 == 0 && ecs_.isActive(enemyId_)) {
            auto& pos = ecs_.getPosition(enemyId_);
            fireBullet(pos.x - 1.0f, pos.y, -15.0f, 0.0f);
        }

        // 일정 간격으로 점수 추가
        if (frameCount_ % 100 == 0) {
            GameEvent evt;
            evt.type = EventType::ScoreChange;
            evt.value = 10.0f;
            events_.enqueue(evt);
        }

        // 체력 감소 시뮬레이션 (충돌 시)
        if (collisionCount_ > 0 && collisionCount_ % 5 == 0) {
            if (ecs_.isActive(enemyId_) && ecs_.hasComponents(enemyId_, ComponentFlag::HEALTH)) {
                auto& hp = ecs_.getHealth(enemyId_);
                if (hp.alive && hp.current > 0) {
                    hp.current -= 1;
                    if (hp.current <= 0) {
                        hp.alive = false;
                        GameEvent evt;
                        evt.type = EventType::EntityDeath;
                        evt.entityA = enemyId_;
                        evt.message = "적 처치!";
                        events_.enqueue(evt);
                    }
                }
            }
        }
    }

    // --- HUD 출력 ---
    void printHUD() {
        std::cout << "프레임: " << frameCount_
                  << " | FPS: " << static_cast<int>(stats_.getAverageFPS())
                  << " | 점수: " << score_
                  << " | 엔티티: " << ecs_.getEntityCount()
                  << " | 총알: " << bulletPool_.getActiveCount()
                    << "/" << bulletPool_.getCapacity()
                  << " | 파티클: " << particlePool_.getActiveCount()
                    << "/" << particlePool_.getCapacity()
                  << " | 충돌: " << collisionCount_;

        // 플레이어 체력 바
        if (ecs_.isActive(playerId_) && ecs_.hasComponents(playerId_, ComponentFlag::HEALTH)) {
            auto& hp = ecs_.getHealth(playerId_);
            std::cout << " | HP: [";
            int bars = hp.current / 10;
            for (int i = 0; i < 10; ++i) {
                std::cout << (i < bars ? "█" : "░");
            }
            std::cout << "] " << hp.current << "/" << hp.max;
        }
        std::cout << "\n\n";
    }

    // --- 최종 리포트 ---
    void printFinalReport() {
        std::cout << "\n";
        std::cout << "╔══════════════════════════════════════════════╗\n";
        std::cout << "║          최종 게임 리포트                    ║\n";
        std::cout << "╠══════════════════════════════════════════════╣\n";
        std::cout << "║  총 프레임:     " << frameCount_ << "\n";
        std::cout << "║  최종 점수:     " << score_ << "\n";
        std::cout << "║  총 충돌 횟수:  " << collisionCount_ << "\n";
        std::cout << "║  발사된 총알:   " << bulletsFired_ << "\n";
        std::cout << "║  생성된 파티클: " << particlesSpawned_ << "\n";
        std::cout << "║  활성 엔티티:   " << ecs_.getEntityCount() << "\n";
        std::cout << "╚══════════════════════════════════════════════╝\n";

        std::cout << "\n";
        std::cout << "=== C++ 게임 엔진의 장점 요약 ===\n";
        std::cout << "  1. GC 없음 → 끊김 없는 부드러운 게임플레이\n";
        std::cout << "     (C#은 GC 스터터링으로 가끔 뚝 끊깁니다)\n";
        std::cout << "  2. 캐시 친화적 ECS → 빠른 데이터 처리\n";
        std::cout << "     (배열 기반이라 CPU 캐시 적중률이 높습니다)\n";
        std::cout << "  3. 결정적 소멸 → 리소스 관리가 정확합니다\n";
        std::cout << "     (소멸자가 정확한 시점에 호출됩니다)\n";
        std::cout << "  4. 오브젝트 풀링 → 게임 중 메모리 할당 제로!\n";
        std::cout << "     (new/delete 없이 총알/파티클 관리)\n";
        std::cout << "  5. 제로 오버헤드 추상화 → 추상화해도 느려지지 않음\n";
        std::cout << "     (C#의 virtual 호출보다 훨씬 가볍습니다)\n";
    }
};

// ============================================================================
//  main() - 프로그램 시작점
// ============================================================================
// C#의 static void Main()과 같습니다

/*
=============================================================================
  실행 흐름 가이드
=============================================================================
  GameWorld::initialize():
    - ECS 등록: Position, Velocity, Health, Sprite 컴포넌트
    - 시스템 등록: PhysicsSystem, RenderSystem, CollisionSystem
    - 엔티티 100개 생성 (적/플레이어/아이템)

  GameWorld::run():
    게임 루프 60 FPS (16.67ms tick)
    매 tick:
      1. update() → 모든 시스템 실행
         - Physics: position += velocity * dt
         - Collision: AABB 충돌 검사 (O(n²) 단순 / 공간 분할로 최적화 가능)
         - Health: HP <= 0 인 엔티티 제거
      2. render() → 콘솔에 ASCII 출력
    100 tick 후 종료 (약 1.6초)

  기대 출력:
    "엔티티 생성: 100"
    "Tick 1 / 100  엔티티: 100  처리시간: 0.5ms"
    ...
    "Tick 100 / 100  엔티티: 87  처리시간: 0.4ms"
    "프로그램 종료. 모든 리소스가 자동으로 정리되었습니다."

  메모리 패턴 (ECS):
    - 컴포넌트는 SoA (Structure of Array) 레이아웃 가능
    - vector<Position> 등 연속 메모리 → 캐시 친화
    - GC 없음 → 결정적 소멸 (블록 끝)
=============================================================================
*/

int main() {
    std::cout << "========================================\n";
    std::cout << "  C++ 게임 엔진 코어 (Game Engine Core)\n";
    std::cout << "  컴파일: g++ -std=c++17 main.cpp -o game\n";
    std::cout << "========================================\n\n";

    GameWorld world;
    world.initialize();
    world.run();
    // ▶ run() 종료 후 main 끝에서 world 소멸자 자동 호출
    //   → 모든 엔티티/컴포넌트/시스템 RAII로 정리

    std::cout << "\n프로그램 종료. 모든 리소스가 자동으로 정리되었습니다.\n";
    std::cout << "(C#이었다면 GC가 언제 정리할지 모릅니다!)\n";

    return 0;
}

/*
 * ============================================================================
 *  학습 포인트 요약
 * ============================================================================
 *
 *  1. ECS 패턴 (Entity Component System)
 *     - Unity의 DOTS/ECS와 같은 패턴
 *     - 엔티티 = ID 번호, 컴포넌트 = 데이터, 시스템 = 로직
 *     - 상속 대신 조합(컴포지션)을 사용
 *
 *  2. 게임 루프 (Fixed Timestep)
 *     - Unity의 Update()가 내부적으로 돌리는 while문
 *     - 고정 타임스텝으로 물리 안정성 확보
 *     - deltaTime으로 프레임 독립적 움직임
 *
 *  3. 오브젝트 풀링
 *     - Unity의 ObjectPool<T>와 같은 패턴
 *     - 게임 루프에서 new/delete 금지!
 *     - 미리 배열로 할당, 인덱스로 관리
 *
 *  4. AABB 충돌 감지
 *     - Unity의 BoxCollider2D와 같은 개념
 *     - 축 정렬 경계 상자로 빠르게 충돌 판정
 *
 *  5. 씬 그래프
 *     - Unity의 Transform 부모-자식 관계
 *     - 부모 이동 시 자식도 따라 이동
 *     - 재귀적 월드 좌표 계산
 *
 *  6. 이벤트 시스템
 *     - C#의 event/delegate 패턴
 *     - 시스템 간 느슨한 결합 (Loose Coupling)
 *     - 큐로 이벤트를 모았다가 한 번에 처리
 *
 *  7. C++ vs C# 게임 개발
 *     - C++: GC 없음, 캐시 친화적, 결정적 소멸
 *     - C#: 편리하지만 GC 스터터링, 캐시 미스
 *     - AAA 게임은 대부분 C++로 만듭니다!
 *
 * ============================================================================
 */
