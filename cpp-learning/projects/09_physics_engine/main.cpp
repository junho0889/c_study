// ============================================================================
// 09_physics_engine/main.cpp
// 2D 물리 엔진 (2D Physics Engine)
// ============================================================================
//
// *** 왜 C++로 물리 엔진을 만들까요? ***
//
// Box2D, Bullet Physics, Havok, PhysX 전부 C++입니다!
// Unity에서 Rigidbody2D를 사용하면, 내부적으로 C++로 만든 물리 엔진이 돌아갑니다!
// 이유: 결정적(deterministic) 실수 연산, SIMD 벡터화, 캐시 친화적 데이터 배치
//
// C#으로도 물리 엔진을 만들 수 있지만, C++은:
//   - GC 멈춤 없이 매 프레임 일정한 시간에 완료
//   - SIMD로 벡터 연산을 4~8배 가속
//   - 메모리를 연속으로 배치해서 CPU 캐시 적중률 극대화
//
// ┌──────────────────────────────────────────────────────┐
// │              2D 물리 엔진 구조도                      │
// │                                                      │
// │  [물리 세계 (World)]                                 │
// │    ├── [강체 (RigidBody)] ← 위치, 속도, 질량        │
// │    │     ├── [힘 적용] ← 중력, 마찰, 스프링, 바람   │
// │    │     └── [적분] ← Semi-implicit Euler 적분법     │
// │    │                                                  │
// │    ├── [충돌 감지 (Broad Phase)] ← 그리드 공간 분할  │
// │    ├── [충돌 감지 (Narrow Phase)]                     │
// │    │     ├── 원-원 충돌                               │
// │    │     ├── AABB-AABB 충돌                           │
// │    │     └── 원-AABB 충돌                             │
// │    │                                                  │
// │    └── [충돌 응답] ← 탄성/비탄성 충돌, 임펄스 해결   │
// └──────────────────────────────────────────────────────┘
//
// ============================================================================

// --- #include 설명 ---
// 각 헤더 파일이 무엇을 하는지 초등학생도 이해할 수 있게 설명합니다!

#include <iostream>      // 화면에 글자를 출력합니다 (cout). C#의 Console.WriteLine!
#include <vector>        // 크기가 변하는 배열. C#의 List<T>와 같아요!
#include <cmath>         // 수학 함수들 (sqrt, sin, cos, abs, floor)
#include <algorithm>     // min, max, clamp, sort 등 편리한 함수
#include <string>        // 문자열 (글자들의 모음). C#의 string!
#include <sstream>       // 문자열을 스트림처럼 읽고 쓸 수 있습니다
#include <iomanip>       // 출력을 예쁘게: 소수점 자릿수 등
#include <unordered_map> // 해시맵 (빠른 키-값 저장). C#의 Dictionary!
#include <unordered_set> // 해시셋 (빠른 중복 없는 집합). C#의 HashSet!
#include <cassert>       // 조건 확인용 (디버그 검증)
#include <chrono>        // 시간 측정. C#의 Stopwatch와 같아요!
#include <random>        // 랜덤 숫자 생성. C#의 Random!
#include <memory>        // 스마트 포인터 (자동 메모리 관리)
#include <numeric>       // 수치 관련 알고리즘 (accumulate 등)

// ============================================================================
// 1. Vec2 수학 라이브러리
// ============================================================================
// Vec2는 Unity의 Vector2와 거의 같습니다!
// 2D 공간에서 위치, 속도, 힘 등을 표현합니다
//
//    y ^        벡터 = 크기(길이)와 방향을 가진 화살표!
//      |  * (3,4)    길이 = sqrt(3^2 + 4^2) = 5
//      |  |          방향 = (3/5, 4/5) = (0.6, 0.8)
//      |  |
//      +--+-------> x
//
// C#에서는: Vector2 v = new Vector2(3, 4);
// C++에서는: Vec2 v(3, 4);
// 거의 똑같죠? 하지만 C++은 스택에 직접 할당되어 더 빠릅니다!

struct Vec2 {
    double x = 0.0, y = 0.0;
    Vec2() = default;
    Vec2(double x, double y) : x(x), y(y) {}

    Vec2 operator+(const Vec2& o) const { return {x+o.x, y+o.y}; }
    Vec2 operator-(const Vec2& o) const { return {x-o.x, y-o.y}; }
    Vec2 operator*(double s) const { return {x*s, y*s}; }
    Vec2 operator/(double s) const { return {x/s, y/s}; }
    Vec2& operator+=(const Vec2& o) { x+=o.x; y+=o.y; return *this; }
    Vec2& operator-=(const Vec2& o) { x-=o.x; y-=o.y; return *this; }
    Vec2& operator*=(double s) { x*=s; y*=s; return *this; }

    // 내적: 두 벡터가 얼마나 같은 방향인지. Unity의 Vector2.Dot()!
    double dot(const Vec2& o) const { return x*o.x + y*o.y; }
    // 2D 외적: 회전 방향 정보
    double cross(const Vec2& o) const { return x*o.y - y*o.x; }
    // 길이: 피타고라스 정리 sqrt(x^2 + y^2)
    double length() const { return std::sqrt(x*x + y*y); }
    double length_squared() const { return x*x + y*y; }
    // 정규화: 길이를 1로. Unity의 Vector2.normalized!
    Vec2 normalized() const {
        double len = length();
        return (len < 1e-10) ? Vec2(0,0) : Vec2(x/len, y/len);
    }
    // 두 점 사이 거리. Unity의 Vector2.Distance()!
    static double distance(const Vec2& a, const Vec2& b) { return (a-b).length(); }
    // 선형 보간 (Lerp)
    static Vec2 lerp(const Vec2& a, const Vec2& b, double t) { return a + (b-a)*t; }

    std::string to_string() const {
        std::ostringstream ss;
        ss << std::fixed << std::setprecision(2) << "(" << x << "," << y << ")";
        return ss.str();
    }
};
Vec2 operator*(double s, const Vec2& v) { return {v.x*s, v.y*s}; }

// ============================================================================
// 2. AABB (Axis-Aligned Bounding Box)
// ============================================================================
// AABB는 Unity의 Bounds와 같습니다
// 회전하지 않는 직사각형으로 빠른 충돌 감지에 사용

struct AABB {
    Vec2 min_point, max_point;
    Vec2 center() const { return (min_point + max_point) * 0.5; }
    Vec2 half_size() const { return (max_point - min_point) * 0.5; }
    double area() const { Vec2 s = max_point-min_point; return s.x*s.y; }
    bool contains(const Vec2& p) const {
        return p.x >= min_point.x && p.x <= max_point.x && p.y >= min_point.y && p.y <= max_point.y;
    }
    bool overlaps(const AABB& o) const {
        return !(max_point.x < o.min_point.x || min_point.x > o.max_point.x ||
                 max_point.y < o.min_point.y || min_point.y > o.max_point.y);
    }
};

// ============================================================================
// 3. 강체 (Rigid Body)
// ============================================================================
// RigidBody는 Unity의 Rigidbody2D와 같은 개념입니다

enum class ShapeType { Circle, Box };

struct RigidBody {
    int id = 0;
    Vec2 position, prev_position, velocity, acceleration, force_accumulator;
    double mass = 1.0, inv_mass = 1.0;
    double restitution = 0.5;  // 반발계수 (0=비탄성, 1=완전탄성)
    double friction = 0.3;
    ShapeType shape = ShapeType::Circle;
    double radius = 0.5;
    Vec2 half_extents;
    bool is_static = false, is_active = true;

    void set_mass(double m) { mass = m; inv_mass = (m > 0) ? (1.0/m) : 0.0; }
    void set_static() { is_static = true; mass = 0; inv_mass = 0; velocity = {0,0}; }
    void apply_force(const Vec2& f) { if (!is_static) force_accumulator += f; }
    void apply_impulse(const Vec2& imp) { if (!is_static) velocity += imp * inv_mass; }
    AABB get_aabb() const {
        if (shape == ShapeType::Circle)
            return {{position.x-radius, position.y-radius}, {position.x+radius, position.y+radius}};
        return {{position.x-half_extents.x, position.y-half_extents.y},
                {position.x+half_extents.x, position.y+half_extents.y}};
    }
};

// ============================================================================
// 4. 힘 생성기 (Force Generators)
// ============================================================================

namespace Forces {
    // 중력: F = m * g. Unity의 Physics2D.gravity!
    void apply_gravity(RigidBody& b, const Vec2& g = {0,-9.81}) {
        if (!b.is_static) b.apply_force(g * b.mass);
    }
    // 마찰력: 속도 반대 방향
    void apply_friction(RigidBody& b, double coeff) {
        if (b.velocity.length_squared() > 1e-10) {
            Vec2 dir = b.velocity.normalized() * (-1.0);
            b.apply_force(dir * (coeff * b.mass * 9.81));
        }
    }
    // 스프링: F = -k * (거리 - 원래길이), 후크의 법칙
    void apply_spring(RigidBody& a, RigidBody& b, double rest, double k, double damp) {
        Vec2 delta = b.position - a.position;
        double dist = delta.length();
        if (dist < 1e-10) return;
        Vec2 dir = delta / dist;
        double stretch = dist - rest;
        double damp_f = damp * (b.velocity - a.velocity).dot(dir);
        Vec2 force = dir * (k * stretch + damp_f);
        a.apply_force(force); b.apply_force(force * (-1.0));
    }
    // 바람: 일정 방향의 힘
    void apply_wind(RigidBody& b, const Vec2& wind) {
        if (!b.is_static) b.apply_force(wind);
    }
}

// ============================================================================
// 5. 충돌 감지 (Collision Detection)
// ============================================================================
//  ○ ○  원-원: 거리 < 반지름 합
//  □ □  AABB-AABB: 겹침 확인
//  ○ □  원-AABB: 가장 가까운 점 계산

struct CollisionInfo {
    bool colliding = false;
    Vec2 normal;
    double penetration = 0.0;
    int body_a_id = -1, body_b_id = -1;
};

class CollisionDetector {
public:
    static CollisionInfo circle_circle(const RigidBody& a, const RigidBody& b) {
        CollisionInfo info; info.body_a_id = a.id; info.body_b_id = b.id;
        Vec2 diff = b.position - a.position;
        double dist = diff.length(), sum_r = a.radius + b.radius;
        if (dist < sum_r) {
            info.colliding = true; info.penetration = sum_r - dist;
            info.normal = (dist > 1e-10) ? (diff/dist) : Vec2(1,0);
        }
        return info;
    }
    static CollisionInfo aabb_aabb(const RigidBody& a, const RigidBody& b) {
        CollisionInfo info; info.body_a_id = a.id; info.body_b_id = b.id;
        Vec2 diff = b.position - a.position;
        double ox = (a.half_extents.x+b.half_extents.x) - std::abs(diff.x);
        double oy = (a.half_extents.y+b.half_extents.y) - std::abs(diff.y);
        if (ox > 0 && oy > 0) {
            info.colliding = true;
            if (ox < oy) { info.penetration = ox; info.normal = (diff.x>=0)?Vec2(1,0):Vec2(-1,0); }
            else { info.penetration = oy; info.normal = (diff.y>=0)?Vec2(0,1):Vec2(0,-1); }
        }
        return info;
    }
    static CollisionInfo circle_aabb(const RigidBody& circ, const RigidBody& box) {
        CollisionInfo info; info.body_a_id = circ.id; info.body_b_id = box.id;
        AABB aabb = box.get_aabb();
        double cx = std::clamp(circ.position.x, aabb.min_point.x, aabb.max_point.x);
        double cy = std::clamp(circ.position.y, aabb.min_point.y, aabb.max_point.y);
        Vec2 diff = circ.position - Vec2(cx, cy);
        double dist = diff.length();
        if (dist < circ.radius) {
            info.colliding = true; info.penetration = circ.radius - dist;
            info.normal = (dist > 1e-10) ? (diff/dist) : Vec2(0,1);
        }
        return info;
    }
    static CollisionInfo detect(const RigidBody& a, const RigidBody& b) {
        if (a.shape == ShapeType::Circle && b.shape == ShapeType::Circle) return circle_circle(a, b);
        if (a.shape == ShapeType::Box && b.shape == ShapeType::Box) return aabb_aabb(a, b);
        if (a.shape == ShapeType::Circle && b.shape == ShapeType::Box) return circle_aabb(a, b);
        auto info = circle_aabb(b, a);
        std::swap(info.body_a_id, info.body_b_id);
        info.normal = info.normal * (-1.0);
        return info;
    }
};

// ============================================================================
// 6. 충돌 응답 (Collision Response)
// ============================================================================
// Physics.Step()은 Unity의 FixedUpdate()에서 내부적으로 호출되는 것입니다!

class CollisionResolver {
public:
    static void resolve(RigidBody& a, RigidBody& b, const CollisionInfo& info) {
        if (!info.colliding) return;
        separate_bodies(a, b, info);
        resolve_impulse(a, b, info);
    }
private:
    // 겹침 해소
    static void separate_bodies(RigidBody& a, RigidBody& b, const CollisionInfo& info) {
        double total = a.inv_mass + b.inv_mass;
        if (total <= 0) return;
        Vec2 correction = info.normal * (info.penetration / total);
        if (!a.is_static) a.position -= correction * a.inv_mass;
        if (!b.is_static) b.position += correction * b.inv_mass;
    }
    // 충격량(임펄스) 기반 속도 변경
    static void resolve_impulse(RigidBody& a, RigidBody& b, const CollisionInfo& info) {
        Vec2 rel_vel = b.velocity - a.velocity;
        double vel_n = rel_vel.dot(info.normal);
        if (vel_n > 0) return;  // 이미 멀어지는 중
        double e = std::min(a.restitution, b.restitution);
        double j = -(1.0 + e) * vel_n / (a.inv_mass + b.inv_mass);
        Vec2 impulse = info.normal * j;
        a.apply_impulse(impulse * (-1.0));
        b.apply_impulse(impulse);
    }
};

// ============================================================================
// 7. 공간 분할 (Spatial Grid) - Broad Phase
// ============================================================================
// 물체가 많을 때 모든 쌍을 검사하면 O(n^2)이라 느립니다
// 그리드로 가까운 물체끼리만 검사 → 훨씬 빠름!
//  ┌───┬───┬───┐
//  │ A │   │ B │  A와 B는 멀어서 검사 안 함!
//  ├───┼───┼───┤
//  │   │C D│   │  C와 D는 같은 셀 → 검사!
//  └───┴───┴───┘

class SpatialGrid {
    double cell_size_;
    std::unordered_map<int64_t, std::vector<int>> cells_;
    int64_t cell_key(int gx, int gy) const { return (int64_t)gx * 100003LL + gy; }
public:
    explicit SpatialGrid(double cs) : cell_size_(cs) {}
    void clear() { cells_.clear(); }
    void insert(const RigidBody& body) {
        AABB aabb = body.get_aabb();
        int x0 = (int)std::floor(aabb.min_point.x/cell_size_), y0 = (int)std::floor(aabb.min_point.y/cell_size_);
        int x1 = (int)std::floor(aabb.max_point.x/cell_size_), y1 = (int)std::floor(aabb.max_point.y/cell_size_);
        for (int gx = x0; gx <= x1; gx++)
            for (int gy = y0; gy <= y1; gy++)
                cells_[cell_key(gx,gy)].push_back(body.id);
    }
    std::vector<std::pair<int,int>> get_potential_pairs() const {
        std::unordered_set<int64_t> seen;
        std::vector<std::pair<int,int>> pairs;
        for (const auto& [key, ids] : cells_) {
            for (size_t i = 0; i < ids.size(); i++)
                for (size_t j = i+1; j < ids.size(); j++) {
                    int a = std::min(ids[i],ids[j]), b = std::max(ids[i],ids[j]);
                    if (seen.insert((int64_t)a*1000000LL+b).second)
                        pairs.push_back({a, b});
                }
        }
        return pairs;
    }
};

// ============================================================================
// 8. 물리 세계 (Physics World)
// ============================================================================
// Physics.Step()은 Unity의 FixedUpdate()에서 내부적으로 호출되는 것입니다!

class PhysicsWorld {
    std::vector<RigidBody> bodies_;
    SpatialGrid grid_;
    Vec2 gravity_;
    int next_id_ = 0, collision_checks_ = 0, collisions_found_ = 0;
public:
    PhysicsWorld(Vec2 g = {0,-9.81}, double cell = 2.0) : grid_(cell), gravity_(g) {}

    int add_body(RigidBody body) {
        body.id = next_id_++;
        body.prev_position = body.position;
        bodies_.push_back(body);
        return body.id;
    }
    RigidBody* get_body(int id) {
        for (auto& b : bodies_) if (b.id == id) return &b;
        return nullptr;
    }
    const std::vector<RigidBody>& bodies() const { return bodies_; }

    void step(double dt) {
        collision_checks_ = 0; collisions_found_ = 0;
        // 1. 힘 적용 (중력)
        for (auto& b : bodies_) if (!b.is_static && b.is_active) Forces::apply_gravity(b, gravity_);
        // 2. 속도 + 위치 갱신 (Semi-implicit Euler)
        for (auto& b : bodies_) {
            if (b.is_static || !b.is_active) continue;
            Vec2 accel = b.force_accumulator * b.inv_mass;
            b.velocity += accel * dt;
            b.prev_position = b.position;
            b.position += b.velocity * dt;
        }
        // 3. 충돌 감지 + 해결
        grid_.clear();
        for (const auto& b : bodies_) if (b.is_active) grid_.insert(b);
        for (const auto& [ia, ib] : grid_.get_potential_pairs()) {
            collision_checks_++;
            RigidBody* a = get_body(ia); RigidBody* b = get_body(ib);
            if (!a || !b) continue;
            CollisionInfo info = CollisionDetector::detect(*a, *b);
            if (info.colliding) { collisions_found_++; CollisionResolver::resolve(*a, *b, info); }
        }
        // 4. 힘 리셋
        for (auto& b : bodies_) b.force_accumulator = {0,0};
    }
    int last_collision_checks() const { return collision_checks_; }
    int last_collisions_found() const { return collisions_found_; }
    int body_count() const { return (int)bodies_.size(); }
};

// ============================================================================
// 데모: 상자 안에서 공 튕기기
// ============================================================================
void run_bouncing_balls_demo() {
    std::cout << "\n=== 상자 안에서 공 튕기기 시뮬레이션 ===\n\n";
    PhysicsWorld world({0,-9.81}, 3.0);

    // 벽 만들기 (고정 물체)
    auto make_wall = [&](Vec2 pos, Vec2 half) {
        RigidBody w; w.position = pos; w.shape = ShapeType::Box;
        w.half_extents = half; w.restitution = 0.8; w.set_static();
        world.add_body(w);
    };
    make_wall({10,-0.5}, {12,0.5});   // 바닥
    make_wall({-0.5,10}, {0.5,12});   // 왼쪽
    make_wall({20.5,10}, {0.5,12});   // 오른쪽
    make_wall({10,20.5}, {12,0.5});   // 천장

    // 공 5개 (랜덤 위치/속도)
    std::mt19937 rng(42);
    std::uniform_real_distribution<double> pd(3.0,17.0), vd(-5.0,5.0);
    std::vector<int> ball_ids;
    for (int i = 0; i < 5; i++) {
        RigidBody ball;
        ball.position = {pd(rng), pd(rng)};
        ball.velocity = {vd(rng), vd(rng)};
        ball.shape = ShapeType::Circle; ball.radius = 0.5;
        ball.set_mass(1.0); ball.restitution = 0.7;
        ball_ids.push_back(world.add_body(ball));
    }

    double dt = 1.0/60.0;
    int total_steps = 300;
    std::cout << "  상자: 20x20, 공: 5개, " << total_steps << "스텝 ("
              << total_steps*dt << "초)\n\n";

    for (int s = 0; s < total_steps; s++) {
        world.step(dt);
        if (s % 60 == 0) {
            std::cout << std::fixed << std::setprecision(2) << "  t=" << s*dt << "s: ";
            for (int id : ball_ids) {
                auto* b = world.get_body(id);
                if (b) std::cout << "공" << (id-3) << b->position.to_string() << " ";
            }
            std::cout << "\n";
        }
    }
    std::cout << "\n  최종:\n";
    for (int id : ball_ids) {
        auto* b = world.get_body(id);
        if (b) std::cout << "    공" << (id-3) << ": 위치" << b->position.to_string()
                         << " 속도" << b->velocity.to_string() << "\n";
    }
}

// ============================================================================
// main 함수
// ============================================================================
/*
=============================================================================
  실행 흐름 가이드
=============================================================================
  [1] Vec2: a=(3,4), b=(1,2)
      a+b=(4,6), a-b=(2,2), a*2=(6,8)
      dot = 3*1 + 4*2 = 11
      cross = 3*2 - 4*1 = 2
      |a| = √(9+16) = 5
      norm = (0.6, 0.8)
      dist = √(4+4) ≈ 2.828
      lerp(0.5) = (2, 3)

  [2] AABB:
      b1[(0,0)~(2,2)]: 중심(1,1), 넓이 4
      b1&b2 겹침: 예 (1~2 영역 공유)
      b1&b3 겹침: 아니오
      (1,1) ∈ b1: 안, (5,5) ∉ b1: 밖

  [3] 충돌 감지:
      원-원 거리 1.5, 반지름합 2 → 충돌, 깊이 0.5
      먼 거리 → 안함
      AABB-AABB 거리 1.5, half-extent 1+1 → 충돌

  [4] 힘과 충돌:
      gravity (0,-9.81) × m=2 = (0,-19.62)
      wind (3,0) → (3,-19.62)
      spring 추가 → 더 복잡한 합
      탄성 충돌: 운동량 + 에너지 보존, restitution=0.8

  [5] 시뮬레이션 (3초, 60Hz):
      t=0: (0,10) 속도(2,0)
      0.5s: 자유낙하 → ~(1,8.8)
      1s: 바운스 시작
      ...

  [6] Spatial Grid: 3개 물체 → 가까운 두 개만 후보 쌍 1개

  [7] BouncingBalls 데모 (별도 함수)

  [8] 벤치마크: 100 물체 × 600 스텝 (10초)
      총: ~수백 ms (단일 스레드)
      충돌 검사 쌍 수, 실제 충돌 발견 수
=============================================================================
*/

int main() {
    std::cout << "============================================================\n";
    std::cout << "  2D 물리 엔진 (2D Physics Engine)\n";
    std::cout << "============================================================\n\n";

    std::cout << "--- 1. Vec2 수학 라이브러리 ---\n";
    {
        Vec2 a(3,4), b(1,2);
        std::cout << "  a=" << a.to_string() << " b=" << b.to_string() << "\n";
        // > 출력:   a=(3, 4) b=(1, 2)
        std::cout << "  a+b=" << (a+b).to_string() << " a-b=" << (a-b).to_string() << "\n";
        // > 출력:   a+b=(4, 6) a-b=(2, 2)
        std::cout << "  a*2=" << (a*2).to_string() << " dot=" << a.dot(b) << " cross=" << a.cross(b) << "\n";
        // → dot = 3*1 + 4*2 = 11, cross = 3*2 - 4*1 = 2
        // > 출력:   a*2=(6, 8) dot=11 cross=2
        std::cout << "  |a|=" << a.length() << " norm=" << a.normalized().to_string() << "\n";
        // → length = √25 = 5, norm = (0.6, 0.8)
        // > 출력:   |a|=5 norm=(0.6, 0.8)
        std::cout << "  dist=" << Vec2::distance(a,b) << " lerp(0.5)=" << Vec2::lerp(a,b,0.5).to_string() << "\n";
        // → dist = √((3-1)²+(4-2)²) = √8 ≈ 2.828
        // → lerp = a + 0.5*(b-a) = (3+(-1), 4+(-1)) = (2, 3)
    }

    // --- 2. AABB ---
    std::cout << "\n--- 2. AABB 충돌 ---\n";
    {
        AABB b1{{0,0},{2,2}}, b2{{1,1},{3,3}}, b3{{5,5},{7,7}};
        std::cout << "  b1 중심:" << b1.center().to_string() << " 넓이:" << b1.area() << "\n";
        std::cout << "  b1&b2 겹침:" << (b1.overlaps(b2)?"예":"아니오")
                  << " b1&b3:" << (b1.overlaps(b3)?"예":"아니오") << "\n";
        std::cout << "  b1에 (1,1):" << (b1.contains({1,1})?"안":"밖")
                  << " (5,5):" << (b1.contains({5,5})?"안":"밖") << "\n";
    }

    // --- 3. 충돌 감지 ---
    std::cout << "\n--- 3. 충돌 감지 ---\n";
    {
        RigidBody c1; c1.id=0; c1.position={0,0}; c1.shape=ShapeType::Circle; c1.radius=1.0;
        RigidBody c2; c2.id=1; c2.position={1.5,0}; c2.shape=ShapeType::Circle; c2.radius=1.0;
        auto i1 = CollisionDetector::circle_circle(c1, c2);
        std::cout << "  원-원(거리1.5, 반지름합2): " << (i1.colliding?"충돌":"안함")
                  << " 깊이:" << i1.penetration << "\n";

        RigidBody c3; c3.id=2; c3.position={5,5}; c3.shape=ShapeType::Circle; c3.radius=1.0;
        std::cout << "  원-원(먼 거리): " << (CollisionDetector::circle_circle(c1,c3).colliding?"충돌":"안함") << "\n";

        RigidBody b1; b1.id=3; b1.position={0,0}; b1.shape=ShapeType::Box; b1.half_extents={1,1};
        RigidBody b2; b2.id=4; b2.position={1.5,0}; b2.shape=ShapeType::Box; b2.half_extents={1,1};
        std::cout << "  AABB-AABB: " << (CollisionDetector::aabb_aabb(b1,b2).colliding?"충돌":"안함") << "\n";
    }

    // --- 4. 힘과 충돌 응답 ---
    std::cout << "\n--- 4. 힘과 충돌 응답 ---\n";
    {
        RigidBody ball; ball.id=0; ball.position={0,10}; ball.set_mass(2.0);
        ball.shape=ShapeType::Circle; ball.radius=0.5;
        Forces::apply_gravity(ball, {0,-9.81});
        std::cout << "  중력 후 힘: " << ball.force_accumulator.to_string() << "\n";
        Forces::apply_wind(ball, {3,0});
        std::cout << "  바람 추가: " << ball.force_accumulator.to_string() << "\n";

        RigidBody anchor; anchor.id=1; anchor.position={5,10}; anchor.set_mass(1.0);
        anchor.shape=ShapeType::Circle; anchor.radius=0.5;
        Forces::apply_spring(ball, anchor, 3.0, 10.0, 0.5);
        std::cout << "  스프링 추가: " << ball.force_accumulator.to_string() << "\n";

        // 충돌 응답
        RigidBody a; a.id=10; a.position={0,0}; a.velocity={5,0}; a.set_mass(1.0);
        a.shape=ShapeType::Circle; a.radius=1.0; a.restitution=0.8;
        RigidBody b; b.id=11; b.position={1.5,0}; b.velocity={-2,0}; b.set_mass(1.0);
        b.shape=ShapeType::Circle; b.radius=1.0; b.restitution=0.8;
        auto info = CollisionDetector::circle_circle(a, b);
        std::cout << "  충돌 전: a=" << a.velocity.to_string() << " b=" << b.velocity.to_string() << "\n";
        CollisionResolver::resolve(a, b, info);
        std::cout << "  충돌 후: a=" << a.velocity.to_string() << " b=" << b.velocity.to_string() << "\n";
    }

    // --- 5. 물리 세계 ---
    std::cout << "\n--- 5. 물리 세계 시뮬레이션 ---\n";
    {
        PhysicsWorld world({0,-9.81}, 2.0);
        RigidBody ground; ground.position={0,-1}; ground.shape=ShapeType::Box;
        ground.half_extents={50,1}; ground.restitution=0.6; ground.set_static();
        world.add_body(ground);

        RigidBody ball; ball.position={0,10}; ball.velocity={2,0};
        ball.shape=ShapeType::Circle; ball.radius=0.5; ball.set_mass(1.0); ball.restitution=0.7;
        int bid = world.add_body(ball);

        std::cout << std::fixed << std::setprecision(2);
        for (int s = 0; s < 180; s++) {
            world.step(1.0/60.0);
            if (s % 30 == 0) {
                auto* b = world.get_body(bid);
                if (b) std::cout << "  t=" << s/60.0 << "s: 위치" << b->position.to_string()
                                 << " 속도" << b->velocity.to_string() << "\n";
            }
        }
    }

    // --- 6. 공간 분할 ---
    std::cout << "\n--- 6. 공간 분할 (그리드) ---\n";
    {
        SpatialGrid grid(5.0);
        RigidBody a; a.id=0; a.position={1,1}; a.shape=ShapeType::Circle; a.radius=0.5;
        RigidBody b; b.id=1; b.position={2,1}; b.shape=ShapeType::Circle; b.radius=0.5;
        RigidBody c; c.id=2; c.position={20,20}; c.shape=ShapeType::Circle; c.radius=0.5;
        grid.insert(a); grid.insert(b); grid.insert(c);
        auto pairs = grid.get_potential_pairs();
        std::cout << "  3개 물체, 후보 쌍: " << pairs.size() << "개\n";
        for (auto& [x,y] : pairs) std::cout << "    " << x << " - " << y << "\n";
    }

    // --- 7. 데모 ---
    run_bouncing_balls_demo();

    // --- 8. 벤치마크 ---
    std::cout << "\n--- 8. 물리 엔진 벤치마크 ---\n";
    {
        PhysicsWorld world({0,-9.81}, 5.0);
        RigidBody ground; ground.position={50,-1}; ground.shape=ShapeType::Box;
        ground.half_extents={60,1}; ground.restitution=0.5; ground.set_static();
        world.add_body(ground);

        std::mt19937 rng(123);
        std::uniform_real_distribution<double> pd(5,95), vd(-10,10);
        for (int i = 0; i < 100; i++) {
            RigidBody b; b.position={pd(rng),pd(rng)}; b.velocity={vd(rng),vd(rng)};
            b.shape=ShapeType::Circle; b.radius=0.5; b.set_mass(1.0); b.restitution=0.6;
            world.add_body(b);
        }
        int steps = 600;
        auto start = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < steps; i++) world.step(1.0/60.0);
        auto end = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration_cast<std::chrono::microseconds>(end-start).count() / 1000.0;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "  물체: " << world.body_count() << ", 스텝: " << steps << "\n";
        std::cout << "  총: " << ms << "ms, 스텝당: " << ms/steps << "ms\n";
        std::cout << "  마지막 충돌검사: " << world.last_collision_checks()
                  << "쌍, 발견: " << world.last_collisions_found() << "건\n";
    }

    // --- 요약 ---
    std::cout << "\n============================================================\n";
    std::cout << "  ** 왜 C++로 물리 엔진을 만들까요? **\n";
    std::cout << "\n";
    std::cout << "  Unity C#에서:\n";
    std::cout << "    Rigidbody2D rb = GetComponent<Rigidbody2D>();\n";
    std::cout << "    rb.AddForce(new Vector2(0, 10));\n";
    std::cout << "  이렇게 간단하게 물리를 쓸 수 있지만...\n";
    std::cout << "\n";
    std::cout << "  내부의 Box2D/PhysX 엔진은 전부 C++!\n";
    std::cout << "\n";
    std::cout << "  C++이 필요한 이유:\n";
    std::cout << "  1. 결정적(deterministic) 실수 연산\n";
    std::cout << "     → 네트워크 게임에서 모든 클라이언트가 동일한 결과\n";
    std::cout << "  2. SIMD로 벡터 연산 4~8배 가속\n";
    std::cout << "     → Vec2 연산을 CPU의 특수 명령어로 한번에 처리\n";
    std::cout << "  3. 캐시 친화적 데이터 배치 (SoA vs AoS)\n";
    std::cout << "     → 메모리를 연속으로 배치해서 CPU 캐시 적중률 극대화\n";
    std::cout << "  4. GC 멈춤 없이 매 프레임 안정적 성능\n";
    std::cout << "     → 16.67ms (60FPS) 안에 반드시 완료해야 함\n";
    std::cout << "============================================================\n";
    return 0;
}
