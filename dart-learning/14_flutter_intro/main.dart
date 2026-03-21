/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Dart 학습 14단계: Flutter 입문
  ─ 위젯 트리 · StatelessWidget · StatefulWidget · BuildContext · 레이아웃 ─

  ■ 실행: dart run main.dart  (콘솔에서 Flutter 개념 시뮬레이션)
  ■ 실제 Flutter: flutter create my_app → flutter run

  ★ 이 파일은 Flutter SDK 없이도 실행 가능하도록
    위젯 개념을 순수 Dart 코드로 시뮬레이션합니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// =====================================================================
// 레슨 1 — Flutter 란?
// =====================================================================
/*
★ Flutter = "Dart 로 만드는 크로스 플랫폼 UI 프레임워크"

  ┌──────────────────────────────────────────────────────────┐
  │  하나의 Dart 코드로:                                     │
  │  ├─ Android 앱                                           │
  │  ├─ iOS 앱                                               │
  │  ├─ 웹 앱                                                │
  │  ├─ Windows/macOS/Linux 데스크톱 앱                      │
  │  └─ 임베디드 (실험적)                                    │
  └──────────────────────────────────────────────────────────┘

★ Flutter vs 다른 프레임워크
  ┌──────────────┬────────────────────────────────────────────┐
  │ 프레임워크   │ 특징                                       │
  ├──────────────┼────────────────────────────────────────────┤
  │ Flutter      │ 자체 렌더링 엔진 (Skia/Impeller)          │
  │ React Native │ 네이티브 컴포넌트 브릿지                   │
  │ Xamarin      │ .NET 기반                                  │
  │ SwiftUI      │ Apple 전용                                 │
  └──────────────┴────────────────────────────────────────────┘

★ Flutter 의 핵심 = "모든 것이 위젯(Widget)"
  - 버튼 → 위젯
  - 텍스트 → 위젯
  - 여백 → 위젯
  - 레이아웃(행, 열) → 위젯
  - 화면 전체 → 위젯들의 트리
*/

void lesson1WhatIsFlutter() {
  print('[레슨 1] Flutter 란?');
  print('  Flutter = Dart 로 만드는 크로스 플랫폼 UI 프레임워크');
  print('  핵심 원칙: "모든 것이 위젯(Widget)"');
  print('  하나의 코드 → Android, iOS, Web, Desktop 전부 지원');
  print('');
}


// =====================================================================
// 레슨 2 — 위젯 트리
// =====================================================================
/*
★ 위젯 트리 = "화면을 나무 구조로 표현한 것"

  비유: 가계도
  - 할아버지(MaterialApp) 아래에 아빠(Scaffold)
  - 아빠 아래에 형(AppBar), 동생(Body)
  - 동생 아래에 자식들(Column → Text, Button)

  ┌──────────────────────────────────────────────────┐
  │  MaterialApp                                     │
  │  └── Scaffold                                    │
  │      ├── AppBar                                  │
  │      │   └── Text('제목')                        │
  │      └── Center                                  │
  │          └── Column                              │
  │              ├── Text('안녕하세요')               │
  │              ├── SizedBox(height: 20)             │
  │              └── ElevatedButton                  │
  │                  └── Text('클릭!')               │
  └──────────────────────────────────────────────────┘

★ 모든 위젯은 build() 메서드로 자신의 모습을 그림
  - build() 가 호출될 때마다 화면이 갱신됨
  - setState() 로 상태가 바뀌면 build() 자동 재호출
*/

class WidgetNode {
  final String name;
  final Map<String, String> props;
  final List<WidgetNode> children;

  WidgetNode(this.name, {
    this.props = const {},
    this.children = const [],
  });
}

void printTree(WidgetNode node, [String prefix = '', bool isLast = true]) {
  final connector = isLast ? '└── ' : '├── ';
  final propStr = node.props.isNotEmpty
      ? '(${node.props.entries.map((e) => '${e.key}: ${e.value}').join(', ')})'
      : '';
  print('$prefix$connector${node.name} $propStr');

  final childPrefix = prefix + (isLast ? '    ' : '│   ');
  for (var i = 0; i < node.children.length; i++) {
    printTree(node.children[i], childPrefix, i == node.children.length - 1);
  }
}

void lesson2WidgetTree() {
  print('[레슨 2] 위젯 트리');

  final app = WidgetNode('MaterialApp', children: [
    WidgetNode('Scaffold', children: [
      WidgetNode('AppBar', children: [
        WidgetNode('Text', props: {'data': "'학습 앱'"}),
      ]),
      WidgetNode('Center', children: [
        WidgetNode('Column', props: {'mainAxisAlignment': 'center'}, children: [
          WidgetNode('Text', props: {'data': "'안녕하세요'"}),
          WidgetNode('SizedBox', props: {'height': '20'}),
          WidgetNode('ElevatedButton', children: [
            WidgetNode('Text', props: {'data': "'클릭!'"}),
          ]),
        ]),
      ]),
    ]),
  ]);

  printTree(app, '', true);
  print('');
}


// =====================================================================
// 레슨 3 — StatelessWidget (상태 없는 위젯)
// =====================================================================
/*
★ StatelessWidget = "한번 만들면 변하지 않는 위젯"

  비유: 액자에 넣은 사진
  - 한번 걸면 그대로 (변하지 않음)
  - 새 사진을 원하면 액자 전체를 바꿔야 함

  ┌──────────────────────────────────────────────────────────┐
  │  class GreetingCard extends StatelessWidget {            │
  │    final String name;                                    │
  │    const GreetingCard({required this.name});             │
  │                                                          │
  │    @override                                             │
  │    Widget build(BuildContext context) {                  │
  │      return Text('안녕하세요, $name님!');                 │
  │    }                                                     │
  │  }                                                       │
  └──────────────────────────────────────────────────────────┘

★ 특징
  - 모든 필드가 final (불변)
  - build() 에서 UI 반환
  - const 생성자 가능 → 성능 최적화
*/

// 콘솔에서 위젯 개념 시뮬레이션
abstract class SimWidget {
  String build();
}

class SimText extends SimWidget {
  final String data;
  final String? style;

  SimText(this.data, {this.style});

  @override
  String build() {
    final styleStr = style != null ? ' ($style)' : '';
    return 'Text("$data"$styleStr)';
  }
}

class SimColumn extends SimWidget {
  final List<SimWidget> children;

  SimColumn(this.children);

  @override
  String build() {
    final childStr = children.map((c) => '    ${c.build()}').join('\n');
    return 'Column(\n$childStr\n  )';
  }
}

// StatelessWidget 시뮬레이션
class ProfileCard extends SimWidget {
  final String name;
  final int age;
  final String hobby;

  ProfileCard({
    required this.name,
    required this.age,
    required this.hobby,
  });

  @override
  String build() {
    return SimColumn([
      SimText(name, style: 'bold, 24pt'),
      SimText('나이: $age살'),
      SimText('취미: $hobby'),
    ]).build();
  }
}

void lesson3Stateless() {
  print('[레슨 3] StatelessWidget (상태 없는 위젯)');

  final card = ProfileCard(name: '민수', age: 20, hobby: '코딩');
  print('  ${card.build()}');
  print('');
  print('  ★ 특징: 모든 필드 final, 한번 만들면 변경 불가');
  print('  ★ 용도: 고정 텍스트, 아이콘, 이미지 등');
  print('');
}


// =====================================================================
// 레슨 4 — StatefulWidget (상태 있는 위젯)
// =====================================================================
/*
★ StatefulWidget = "사용자 상호작용으로 변하는 위젯"

  비유: 자판기
  - 버튼 누르면 표시 숫자가 바뀜
  - 내부 상태(선택된 음료, 투입 금액) 가 변함

  ┌──────────────────────────────────────────────────────────┐
  │  class Counter extends StatefulWidget {                  │
  │    @override                                             │
  │    State<Counter> createState() => _CounterState();      │
  │  }                                                       │
  │                                                          │
  │  class _CounterState extends State<Counter> {            │
  │    int _count = 0;           ← 변하는 상태               │
  │                                                          │
  │    @override                                             │
  │    Widget build(BuildContext context) {                  │
  │      return Column(children: [                           │
  │        Text('$_count'),                                  │
  │        ElevatedButton(                                   │
  │          onPressed: () {                                 │
  │            setState(() { _count++; });  ← 상태 변경!     │
  │          },                                              │
  │        ),                                                │
  │      ]);                                                 │
  │    }                                                     │
  │  }                                                       │
  └──────────────────────────────────────────────────────────┘

★ setState() 가 호출되면:
  1. 상태 값 변경
  2. build() 자동 재호출
  3. 화면 갱신

★ 주의: setState() 안에서 비동기 작업 금지!
  setState() 는 동기적으로 상태만 바꾸는 용도
*/

// StatefulWidget 시뮬레이션
class CounterSimulator {
  int _count = 0;

  int get count => _count;

  // setState 시뮬레이션
  void increment() {
    _count++;
    _rebuild();
  }

  void decrement() {
    if (_count > 0) _count--;
    _rebuild();
  }

  void _rebuild() {
    // Flutter 에서는 여기서 build() 가 다시 호출되어 화면 갱신
    print('    [rebuild] 카운터: $_count');
  }

  String build() {
    return 'Column(\n'
        '    Text("카운터: $_count"),\n'
        '    Row(\n'
        '      ElevatedButton("+")\n'
        '      ElevatedButton("-")\n'
        '    )\n'
        '  )';
  }
}

void lesson4Stateful() {
  print('[레슨 4] StatefulWidget (상태 있는 위젯)');

  final counter = CounterSimulator();
  print('  초기 상태:');
  print('  ${counter.build()}');

  print('  --- 버튼 클릭 시뮬레이션 ---');
  counter.increment();   // 1
  counter.increment();   // 2
  counter.increment();   // 3
  counter.decrement();   // 2

  print('  최종 카운터: ${counter.count}');
  print('');
}


// =====================================================================
// 레슨 5 — 위젯 생명주기
// =====================================================================
/*
★ StatefulWidget 의 생명주기

  ┌──────────────────────────────────────────────────────────┐
  │  createState()     ← State 객체 생성                     │
  │       ↓                                                  │
  │  initState()       ← 초기화 (API 호출, 구독 등)          │
  │       ↓                                                  │
  │  didChangeDependencies() ← 의존성 변경 시                │
  │       ↓                                                  │
  │  build()           ← UI 그리기 (가장 자주 호출)          │
  │       ↓                                                  │
  │  didUpdateWidget() ← 부모가 새 위젯 전달 시              │
  │       ↓                                                  │
  │  setState()  ───→  build()  (상태 변경 시 반복)          │
  │       ↓                                                  │
  │  deactivate()      ← 트리에서 제거 시                    │
  │       ↓                                                  │
  │  dispose()         ← 영구 제거 (리소스 해제!)            │
  └──────────────────────────────────────────────────────────┘

★ 중요 포인트
  - initState: 한 번만 호출, super.initState() 먼저!
  - dispose: 한 번만 호출, 컨트롤러/스트림 구독 해제
  - build: 여러 번 호출될 수 있으므로 가볍게!
*/

class LifecycleSimulator {
  String _state = 'created';
  final List<String> _history = [];

  void _log(String phase) {
    _state = phase;
    _history.add(phase);
  }

  void createState() => _log('createState');
  void initState() => _log('initState');
  void build() => _log('build');
  void setState() {
    _log('setState');
    build();   // setState 후 자동 build
  }
  void deactivate() => _log('deactivate');
  void dispose() => _log('dispose');

  void printHistory() {
    for (var i = 0; i < _history.length; i++) {
      final arrow = i < _history.length - 1 ? ' →' : ' ■';
      print('    ${i + 1}. ${_history[i]}$arrow');
    }
  }
}

void lesson5Lifecycle() {
  print('[레슨 5] 위젯 생명주기');

  final sim = LifecycleSimulator();

  sim.createState();
  sim.initState();
  sim.build();          // 첫 렌더링
  sim.setState();       // 상태 변경 → build 자동 호출
  sim.setState();       // 또 변경
  sim.deactivate();
  sim.dispose();

  print('  생명주기 흐름:');
  sim.printHistory();
  print('');
}


// =====================================================================
// 레슨 6 — 레이아웃 위젯
// =====================================================================
/*
★ Flutter 레이아웃 위젯 TOP 10

  ┌───────────────┬──────────────────────────────────────────┐
  │ 위젯          │ 역할                                     │
  ├───────────────┼──────────────────────────────────────────┤
  │ Container     │ 박스 (패딩, 마진, 색상, 크기)            │
  │ Row           │ 가로 정렬                                │
  │ Column        │ 세로 정렬                                │
  │ Stack         │ 겹치기 (Z축)                             │
  │ ListView      │ 스크롤 가능 리스트                       │
  │ GridView      │ 격자 배치                                │
  │ Padding       │ 안쪽 여백                                │
  │ SizedBox      │ 고정 크기 공간                           │
  │ Expanded      │ 남은 공간 채우기                         │
  │ Center        │ 가운데 정렬                              │
  └───────────────┴──────────────────────────────────────────┘

★ Row 와 Column 의 정렬

  mainAxisAlignment (주축):
  ┌─────────────────────────────────────────┐
  │  start    center    end    spaceBetween │
  │  ○○○___   ___○○○___  ___○○○  ○___○___○ │
  └─────────────────────────────────────────┘

  crossAxisAlignment (교차축):
  ┌───────────────────────────────┐
  │  start   center   end        │
  │  ○       ___○     ______○    │
  │  ○       ___○     ______○    │
  └───────────────────────────────┘
*/

void lesson6Layout() {
  print('[레슨 6] 레이아웃 위젯');

  print('  ★ 가장 많이 쓰는 레이아웃 패턴:');
  print('');

  // 실제 Flutter 코드 예시 출력
  print('  // 로그인 화면 예시');
  print('  Scaffold(');
  print('    body: Center(');
  print('      child: Column(');
  print('        mainAxisAlignment: MainAxisAlignment.center,');
  print('        children: [');
  print('          Text("로그인", style: TextStyle(fontSize: 24)),');
  print('          SizedBox(height: 20),');
  print('          TextField(decoration: InputDecoration(label: Text("이메일"))),');
  print('          SizedBox(height: 10),');
  print('          TextField(obscureText: true),');
  print('          SizedBox(height: 20),');
  print('          ElevatedButton(onPressed: login, child: Text("로그인")),');
  print('        ],');
  print('      ),');
  print('    ),');
  print('  )');
  print('');
}


// =====================================================================
// 레슨 7 — 네비게이션 (화면 이동)
// =====================================================================
/*
★ Flutter 네비게이션 = "화면(Route) 을 스택으로 관리"

  비유: 카드 더미
  ┌──────────────────────────────────────────────────┐
  │  push → 새 카드를 위에 올림 (새 화면)            │
  │  pop  → 맨 위 카드 제거 (이전 화면으로)          │
  │                                                  │
  │  ┌────────────┐                                  │
  │  │ 상세 화면  │  ← 현재 보이는 화면              │
  │  ├────────────┤                                  │
  │  │ 목록 화면  │                                  │
  │  ├────────────┤                                  │
  │  │ 홈 화면    │  ← 가장 처음 화면                │
  │  └────────────┘                                  │
  └──────────────────────────────────────────────────┘

★ 네비게이션 코드
  // 새 화면으로 이동
  Navigator.push(context, MaterialPageRoute(
    builder: (context) => DetailPage(),
  ));

  // 이전 화면으로 돌아가기
  Navigator.pop(context);

  // 이름으로 이동 (Named Route)
  Navigator.pushNamed(context, '/detail');
*/

class NavigationSimulator {
  final List<String> _stack = ['Home'];

  String get currentPage => _stack.last;
  int get depth => _stack.length;

  void push(String page) {
    _stack.add(page);
    print('    push → $page (스택 깊이: $depth)');
  }

  void pop() {
    if (_stack.length <= 1) {
      print('    pop 불가: 마지막 화면입니다!');
      return;
    }
    final removed = _stack.removeLast();
    print('    pop ← $removed → 현재: $currentPage');
  }

  void printStack() {
    print('    화면 스택:');
    for (var i = _stack.length - 1; i >= 0; i--) {
      final marker = i == _stack.length - 1 ? ' ← 현재' : '';
      print('      [$i] ${_stack[i]}$marker');
    }
  }
}

void lesson7Navigation() {
  print('[레슨 7] 네비게이션 (화면 이동)');

  final nav = NavigationSimulator();
  nav.push('ProductList');
  nav.push('ProductDetail');
  nav.push('Cart');

  nav.printStack();

  nav.pop();   // Cart 제거
  nav.pop();   // ProductDetail 제거

  nav.printStack();
  print('');
}


// =====================================================================
// 레슨 8 — Flutter 프로젝트 시작하기
// =====================================================================
/*
★ Flutter 프로젝트 생성 & 실행

  ┌──────────────────────────────────────────────────────────┐
  │  # 1. Flutter 설치 (flutter.dev 에서 다운로드)           │
  │  flutter doctor           ← 환경 점검                    │
  │                                                          │
  │  # 2. 프로젝트 생성                                      │
  │  flutter create my_app                                   │
  │                                                          │
  │  # 3. 실행                                               │
  │  cd my_app                                               │
  │  flutter run              ← 에뮬레이터/실기기에서 실행    │
  │                                                          │
  │  # 4. 핫 리로드 (코드 수정 즉시 반영)                    │
  │  r   → 핫 리로드                                         │
  │  R   → 핫 리스타트                                       │
  │  q   → 종료                                              │
  └──────────────────────────────────────────────────────────┘

★ 프로젝트 구조
  ┌──────────────────────────────────────────────────┐
  │  my_app/                                         │
  │  ├── lib/                 ← Dart 코드            │
  │  │   └── main.dart        ← 앱 진입점            │
  │  ├── test/                ← 테스트               │
  │  ├── android/             ← 안드로이드 네이티브   │
  │  ├── ios/                 ← iOS 네이티브          │
  │  ├── web/                 ← 웹                    │
  │  ├── pubspec.yaml         ← 패키지 설정          │
  │  └── analysis_options.yaml                       │
  └──────────────────────────────────────────────────┘

★ 첫 번째 Flutter 앱 코드 (실제 코드)

  import 'package:flutter/material.dart';

  void main() => runApp(const MyApp());

  class MyApp extends StatelessWidget {
    const MyApp({super.key});

    @override
    Widget build(BuildContext context) {
      return MaterialApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('첫 Flutter 앱')),
          body: const Center(
            child: Text('안녕하세요, Flutter!'),
          ),
        ),
      );
    }
  }
*/

void lesson8GettingStarted() {
  print('[레슨 8] Flutter 프로젝트 시작하기');

  print('  1. flutter doctor     → 환경 점검');
  print('  2. flutter create app → 프로젝트 생성');
  print('  3. flutter run        → 앱 실행');
  print('  4. r 키               → 핫 리로드 (즉시 반영!)');
  print('');
  print('  ★ Flutter 의 킬러 기능: 핫 리로드');
  print('    코드를 수정하고 저장하면 1초 안에 화면에 반영!');
  print('    앱을 처음부터 다시 빌드할 필요 없음');
  print('');
}


// =====================================================================
// main — 전체 레슨 실행
// =====================================================================
void main() {
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('  Dart 14단계 : Flutter 입문');
  print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■');
  print('');

  lesson1WhatIsFlutter();
  lesson2WidgetTree();
  lesson3Stateless();
  lesson4Stateful();
  lesson5Lifecycle();
  lesson6Layout();
  lesson7Navigation();
  lesson8GettingStarted();

  print('■■■ 14단계 완료! ■■■');
}
