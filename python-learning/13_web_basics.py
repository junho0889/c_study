# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
#
#   파이썬 학습 13단계: 웹 기초
#   ─ HTTP, 소켓, 라우팅, 템플릿, REST API, 미들웨어, 세션, 미니 프레임워크 ─
#   ■ 실행 방법: python 13_web_basics.py
#
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


# ─────────────────────────────────────────────────────────────────────────
# ■ 레슨 목록
# ─────────────────────────────────────────────────────────────────────────
#
#   1. HTTP 프로토콜 이해 — 요청/응답 구조, 헤더, 바디, 상태코드
#   2. 소켓으로 HTTP 맛보기 — socket으로 간단한 웹서버 시뮬레이션
#   3. 라우팅 시스템 만들기 — URL→함수 매핑, 경로 파라미터, 쿼리 스트링
#   4. 템플릿 엔진 개념 — 문자열 치환으로 HTML 생성
#   5. REST API 개념 — CRUD→HTTP 매핑, JSON 요청/응답
#   6. 요청 파싱 — GET/POST 파라미터, Content-Type, URL 디코딩
#   7. 미들웨어 개념 — 요청/응답 전후 처리, 로깅, 인증
#   8. 세션과 쿠키 개념 — 상태 관리, 세션 저장소
#   9. 실전: 미니 웹 프레임워크 만들기 (Flask 스타일)
#
# ─────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import hashlib
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Any
from urllib.parse import parse_qs, unquote


# =========================================================================
#
#   레슨 1 — HTTP 프로토콜 이해
#
# =========================================================================

def lesson1_http_protocol():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 1 : HTTP 프로토콜 이해           │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ HTTP란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   HTTP = HyperText Transfer Protocol
    #   웹에서 클라이언트(브라우저)와 서버가 대화하는 약속입니다.
    #
    #   비유: 레스토랑 주문 시스템
    #     - 클라이언트(손님) → "메뉴 보여주세요" (요청/Request)
    #     - 서버(주방)       → "여기 메뉴입니다" (응답/Response)
    #     - 메뉴판(URL)      → /menu, /order, /bill
    #     - 주문서(HTTP 메서드) → GET(보기), POST(주문), DELETE(취소)
    #

    # ─── HTTP 요청 구조 ───

    print("  ■ HTTP 요청 (Request) 구조:")
    print()
    print("    ┌─────────────────────────────────────────┐")
    print("    │  GET /students?grade=3 HTTP/1.1          │ ← 요청 라인")
    print("    │  Host: school.example.com                │ ← 헤더")
    print("    │  Accept: application/json                │")
    print("    │  Authorization: Bearer abc123            │")
    print("    │                                          │ ← 빈 줄")
    print("    │  (요청 바디 — GET에는 보통 없음)          │ ← 바디")
    print("    └─────────────────────────────────────────┘")
    print()

    # ─── HTTP 응답 구조 ───

    print("  ■ HTTP 응답 (Response) 구조:")
    print()
    print("    ┌─────────────────────────────────────────┐")
    print("    │  HTTP/1.1 200 OK                        │ ← 상태 라인")
    print("    │  Content-Type: application/json          │ ← 헤더")
    print("    │  Content-Length: 45                      │")
    print("    │                                          │ ← 빈 줄")
    print('    │  {"students": [{"name": "민수"}]}        │ ← 바디')
    print("    └─────────────────────────────────────────┘")
    print()

    # ─── HTTP 메서드 ───

    print("  ■ HTTP 메서드 (동사):")
    methods = [
        ("GET", "데이터 조회", "메뉴판 보기"),
        ("POST", "데이터 생성", "새 주문하기"),
        ("PUT", "데이터 전체 수정", "주문 전체 변경"),
        ("PATCH", "데이터 부분 수정", "사이드 메뉴만 변경"),
        ("DELETE", "데이터 삭제", "주문 취소"),
    ]
    print(f"    {'메서드':<8} {'의미':^14} {'비유':>16}")
    print(f"    {'─' * 8} {'─' * 14} {'─' * 16}")
    for method, meaning, analogy in methods:
        print(f"    {method:<8} {meaning:^14} {analogy:>16}")
    print()

    # ─── 주요 상태 코드 ───

    print("  ■ 주요 HTTP 상태 코드:")
    codes = [
        (200, "OK", "요청 성공"),
        (201, "Created", "새로 생성됨"),
        (204, "No Content", "성공, 반환할 내용 없음"),
        (301, "Moved Permanently", "영구 이동"),
        (400, "Bad Request", "잘못된 요청"),
        (401, "Unauthorized", "인증 필요"),
        (403, "Forbidden", "접근 거부"),
        (404, "Not Found", "찾을 수 없음"),
        (500, "Internal Server Error", "서버 내부 에러"),
    ]
    for code, text, desc in codes:
        emoji = "○" if code < 300 else ("△" if code < 400 else "✗")
        print(f"    {emoji} {code} {text:<25} — {desc}")
    print()


# =========================================================================
#
#   레슨 2 — 소켓으로 HTTP 맛보기
#
# =========================================================================

def lesson2_socket_http():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 2 : 소켓으로 HTTP 맛보기         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 소켓이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   소켓 = 네트워크 통신의 양 끝점 (전화기 같은 것!)
    #
    #   비유: 두 사람이 전화 통화하려면
    #     → 각자 전화기(소켓)가 있어야 하고
    #     → 전화번호(IP + 포트)를 알아야 합니다
    #
    #   웹서버도 결국 소켓으로 통신합니다!
    #   Flask, Django 등의 프레임워크가 이걸 편하게 해주는 것입니다.
    #
    #   ★ 여기서는 실제 서버를 띄우지 않고, HTTP 메시지를 문자열로 만들어 봅니다.
    #

    # ─── HTTP 요청 메시지 만들기 ───

    print("  ─── HTTP 요청 메시지 만들기 ───")

    def build_http_request(method: str, path: str, headers: dict = None,
                           body: str = "") -> str:
        """HTTP 요청 메시지를 문자열로 생성합니다."""
        request_line = f"{method} {path} HTTP/1.1"
        header_lines = []
        if headers:
            for key, value in headers.items():
                header_lines.append(f"{key}: {value}")
        if body:
            header_lines.append(f"Content-Length: {len(body.encode())}")

        message = request_line + "\r\n"
        message += "\r\n".join(header_lines) + "\r\n"
        message += "\r\n"  # 빈 줄 (헤더와 바디 구분)
        message += body
        return message

    get_request = build_http_request(
        "GET", "/students",
        headers={"Host": "school.example.com", "Accept": "application/json"}
    )
    print(f"  GET 요청:\n{get_request}")

    post_body = json.dumps({"name": "민수", "grade": 3})
    post_request = build_http_request(
        "POST", "/students",
        headers={"Host": "school.example.com", "Content-Type": "application/json"},
        body=post_body
    )
    print(f"  POST 요청:\n{post_request}")

    # ─── HTTP 응답 메시지 만들기 ───

    print("  ─── HTTP 응답 메시지 만들기 ───")

    def build_http_response(status_code: int, status_text: str,
                            body: str, content_type: str = "application/json") -> str:
        """HTTP 응답 메시지를 문자열로 생성합니다."""
        status_line = f"HTTP/1.1 {status_code} {status_text}"
        headers = [
            f"Content-Type: {content_type}",
            f"Content-Length: {len(body.encode())}",
        ]
        message = status_line + "\r\n"
        message += "\r\n".join(headers) + "\r\n"
        message += "\r\n"
        message += body
        return message

    response = build_http_response(
        200, "OK",
        json.dumps({"students": [{"name": "민수"}, {"name": "지유"}]}, ensure_ascii=False)
    )
    print(f"  응답:\n{response}")

    # ─── 간단한 웹서버 구조 설명 ───

    print("  ─── 실제 웹서버의 기본 구조 ───")
    print()
    print("    import socket")
    print()
    print("    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)")
    print("    server.bind(('localhost', 8080))")
    print("    server.listen(5)")
    print()
    print("    while True:")
    print("        client, addr = server.accept()  # 연결 대기")
    print("        data = client.recv(1024)         # 요청 수신")
    print("        # ... 요청 처리 ...")
    print("        client.send(response.encode())   # 응답 전송")
    print("        client.close()")
    print()


# =========================================================================
#
#   레슨 3 — 라우팅 시스템 만들기
#
# =========================================================================

def lesson3_routing():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 3 : 라우팅 시스템 만들기         │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 라우팅이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   URL → 함수 매핑
    #
    #   비유: 전화 교환대
    #     → "내선 101번"으로 전화 → 영업부로 연결
    #     → "내선 102번"으로 전화 → 기술부로 연결
    #     → URL이 "내선번호", 함수가 "부서"
    #

    class Router:
        def __init__(self):
            self.routes: list[tuple[str, str, Callable]] = []

        def add_route(self, method: str, pattern: str, handler: Callable):
            """라우트를 등록합니다."""
            self.routes.append((method, pattern, handler))

        def route(self, method: str, path: str) -> dict:
            """URL과 메서드에 맞는 핸들러를 찾아 실행합니다."""
            # 쿼리 스트링 분리
            query_string = ""
            if "?" in path:
                path, query_string = path.split("?", 1)

            query_params = parse_qs(query_string)

            for route_method, pattern, handler in self.routes:
                if route_method != method:
                    continue

                # 경로 파라미터 매칭 (/students/<name> 같은 패턴)
                regex = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern)
                match = re.fullmatch(regex, path)

                if match:
                    path_params = match.groupdict()
                    return handler(path_params=path_params, query_params=query_params)

            return {"status": 404, "body": {"error": "Not Found"}}

    # ─── 라우터 구성 ───

    router = Router()

    # 학생 데이터
    students_db = [
        {"name": "민수", "grade": 3, "score": 95},
        {"name": "지유", "grade": 4, "score": 88},
        {"name": "서연", "grade": 3, "score": 78},
    ]

    def get_students(path_params, query_params):
        """전체 학생 목록 (필터링 가능)."""
        result = students_db
        if "grade" in query_params:
            grade = int(query_params["grade"][0])
            result = [s for s in result if s["grade"] == grade]
        return {"status": 200, "body": {"students": result, "count": len(result)}}

    def get_student_by_name(path_params, query_params):
        """이름으로 학생 조회."""
        name = unquote(path_params["name"])
        student = next((s for s in students_db if s["name"] == name), None)
        if student:
            return {"status": 200, "body": student}
        return {"status": 404, "body": {"error": f"'{name}' 학생을 찾을 수 없습니다"}}

    def get_health(path_params, query_params):
        """서버 상태 확인."""
        return {"status": 200, "body": {"status": "healthy"}}

    router.add_route("GET", "/students", get_students)
    router.add_route("GET", "/students/<name>", get_student_by_name)
    router.add_route("GET", "/health", get_health)

    # ─── 라우팅 테스트 ───

    print("  ─── 라우팅 테스트 ───")

    test_requests = [
        ("GET", "/students"),
        ("GET", "/students?grade=3"),
        ("GET", "/students/민수"),
        ("GET", "/students/없는학생"),
        ("GET", "/health"),
        ("GET", "/unknown"),
    ]

    for method, path in test_requests:
        result = router.route(method, path)
        print(f"  {method} {path}")
        print(f"    → [{result['status']}] {result['body']}")
    print()


# =========================================================================
#
#   레슨 4 — 템플릿 엔진 개념
#
# =========================================================================

def lesson4_template_engine():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 4 : 템플릿 엔진 개념             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 템플릿 엔진이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   HTML 뼈대에 데이터를 끼워 넣어 완성된 페이지를 만드는 것입니다.
    #
    #   비유: 편지 양식
    #     "친애하는 {{ name }}님, {{ item }}을 주문해 주셔서 감사합니다."
    #     → name="민수", item="책"을 넣으면
    #     → "친애하는 민수님, 책을 주문해 주셔서 감사합니다."
    #

    # ─── 간단한 템플릿 엔진 구현 ───

    def render_template(template: str, context: dict) -> str:
        """{{ 변수명 }} 형태의 템플릿을 렌더링합니다."""
        result = template
        for key, value in context.items():
            result = result.replace("{{ " + key + " }}", str(value))
        return result

    # ─── HTML 템플릿 예시 ───

    html_template = """<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>{{ heading }}</h1>
    <p>안녕하세요, {{ name }}님!</p>
    <p>현재 등급: {{ grade }}학년</p>
    <p>평균 점수: {{ score }}점</p>
</body>
</html>"""

    rendered = render_template(html_template, {
        "title": "학생 정보",
        "heading": "학생 프로필",
        "name": "민수",
        "grade": "3",
        "score": "95",
    })

    print("  ─── 템플릿 렌더링 결과 ───")
    for line in rendered.strip().split("\n"):
        print(f"  {line}")
    print()

    # ─── 반복 렌더링 (리스트) ───

    print("  ─── 리스트 렌더링 ───")

    def render_list(template: str, items: list[dict]) -> str:
        """리스트의 각 항목을 템플릿에 적용합니다."""
        rendered_items = []
        for item in items:
            rendered_items.append(render_template(template, item))
        return "\n".join(rendered_items)

    row_template = "    <tr><td>{{ name }}</td><td>{{ score }}점</td></tr>"
    students = [
        {"name": "민수", "score": "95"},
        {"name": "지유", "score": "88"},
        {"name": "서연", "score": "78"},
    ]

    table_body = render_list(row_template, students)
    print("  <table>")
    print("    <tr><th>이름</th><th>점수</th></tr>")
    print(table_body)
    print("  </table>")
    print()

    # ─── 조건부 렌더링 ───

    print("  ─── 조건부 렌더링 (간단 버전) ───")

    def render_with_condition(template: str, context: dict,
                              conditions: dict[str, bool] = None) -> str:
        """조건에 따라 섹션을 보이거나 숨깁니다."""
        result = render_template(template, context)
        if conditions:
            for key, show in conditions.items():
                tag_start = f"<!-- if {key} -->"
                tag_end = f"<!-- endif {key} -->"
                if not show:
                    # 조건이 False이면 해당 섹션 제거
                    while tag_start in result and tag_end in result:
                        start = result.index(tag_start)
                        end = result.index(tag_end) + len(tag_end)
                        result = result[:start] + result[end:]
                else:
                    result = result.replace(tag_start, "").replace(tag_end, "")
        return result

    cond_template = """<div>
  <h1>{{ name }}</h1>
  <!-- if is_vip --><span class="badge">VIP 회원</span><!-- endif is_vip -->
  <p>점수: {{ score }}</p>
</div>"""

    vip_result = render_with_condition(cond_template,
                                       {"name": "민수", "score": "95"},
                                       {"is_vip": True})
    normal_result = render_with_condition(cond_template,
                                          {"name": "서연", "score": "78"},
                                          {"is_vip": False})

    print("  VIP 회원:")
    for line in vip_result.strip().split("\n"):
        print(f"    {line}")
    print("  일반 회원:")
    for line in normal_result.strip().split("\n"):
        print(f"    {line}")
    print()


# =========================================================================
#
#   레슨 5 — REST API 개념
#
# =========================================================================

def lesson5_rest_api():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 5 : REST API 개념               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ REST API란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   REST = Representational State Transfer
    #   웹에서 데이터를 주고받는 설계 규칙입니다.
    #
    #   핵심 원칙:
    #   1. URL은 자원(resource)을 나타냄  (/students, /books)
    #   2. HTTP 메서드는 동작을 나타냄    (GET, POST, PUT, DELETE)
    #   3. 상태 코드로 결과를 알려줌       (200, 201, 404, 500)
    #   4. JSON으로 데이터를 주고받음
    #
    #   비유: 도서관 시스템
    #     GET    /books      → 책 목록 보기
    #     GET    /books/42   → 42번 책 상세 보기
    #     POST   /books      → 새 책 등록
    #     PUT    /books/42   → 42번 책 정보 수정
    #     DELETE /books/42   → 42번 책 삭제
    #

    print("  ■ CRUD → HTTP 매핑:")
    print(f"    {'CRUD':<10} {'HTTP 메서드':<12} {'URL 예시':<20} {'설명'}")
    print(f"    {'─' * 10} {'─' * 12} {'─' * 20} {'─' * 15}")
    print(f"    {'Create':<10} {'POST':<12} {'POST /students':<20} {'학생 생성'}")
    print(f"    {'Read':<10} {'GET':<12} {'GET /students':<20} {'목록 조회'}")
    print(f"    {'Read':<10} {'GET':<12} {'GET /students/1':<20} {'단건 조회'}")
    print(f"    {'Update':<10} {'PUT':<12} {'PUT /students/1':<20} {'전체 수정'}")
    print(f"    {'Delete':<10} {'DELETE':<12} {'DELETE /students/1':<20} {'삭제'}")
    print()

    # ─── 시뮬레이션으로 REST API 실습 ───

    class RestApi:
        def __init__(self):
            self.data = {}
            self.next_id = 1

        def handle(self, method: str, path: str, body: dict = None) -> dict:
            parts = path.strip("/").split("/")
            resource = parts[0] if parts else ""
            resource_id = int(parts[1]) if len(parts) > 1 else None

            if method == "GET" and resource_id is None:
                # 목록 조회
                items = list(self.data.values())
                return {"status": 200, "body": items}

            elif method == "GET" and resource_id is not None:
                # 단건 조회
                if resource_id in self.data:
                    return {"status": 200, "body": self.data[resource_id]}
                return {"status": 404, "body": {"error": "Not Found"}}

            elif method == "POST":
                # 생성
                item = {**(body or {}), "id": self.next_id}
                self.data[self.next_id] = item
                self.next_id += 1
                return {"status": 201, "body": item}

            elif method == "PUT" and resource_id is not None:
                # 수정
                if resource_id not in self.data:
                    return {"status": 404, "body": {"error": "Not Found"}}
                self.data[resource_id] = {**(body or {}), "id": resource_id}
                return {"status": 200, "body": self.data[resource_id]}

            elif method == "DELETE" and resource_id is not None:
                # 삭제
                if resource_id not in self.data:
                    return {"status": 404, "body": {"error": "Not Found"}}
                deleted = self.data.pop(resource_id)
                return {"status": 200, "body": deleted}

            return {"status": 400, "body": {"error": "Bad Request"}}

    api = RestApi()

    print("  ─── REST API 시뮬레이션 ───")

    # Create
    r = api.handle("POST", "/students", {"name": "민수", "grade": 3})
    print(f"  POST /students → [{r['status']}] {r['body']}")

    r = api.handle("POST", "/students", {"name": "지유", "grade": 4})
    print(f"  POST /students → [{r['status']}] {r['body']}")

    # Read all
    r = api.handle("GET", "/students")
    print(f"  GET /students → [{r['status']}] {r['body']}")

    # Read one
    r = api.handle("GET", "/students/1")
    print(f"  GET /students/1 → [{r['status']}] {r['body']}")

    # Update
    r = api.handle("PUT", "/students/1", {"name": "민수", "grade": 4})
    print(f"  PUT /students/1 → [{r['status']}] {r['body']}")

    # Delete
    r = api.handle("DELETE", "/students/2")
    print(f"  DELETE /students/2 → [{r['status']}] {r['body']}")

    # Read all after changes
    r = api.handle("GET", "/students")
    print(f"  GET /students → [{r['status']}] {r['body']}")
    print()


# =========================================================================
#
#   레슨 6 — 요청 파싱
#
# =========================================================================

def lesson6_request_parsing():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 6 : 요청 파싱                   │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 요청 파싱이란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   클라이언트가 보낸 HTTP 요청 문자열을 분석해서
    #   메서드, 경로, 헤더, 바디 등으로 나누는 것입니다.
    #

    @dataclass
    class ParsedRequest:
        method: str
        path: str
        query_params: dict
        headers: dict
        body: str
        json_body: dict | None = None

    def parse_request(raw: str) -> ParsedRequest:
        """HTTP 요청 문자열을 파싱합니다."""
        parts = raw.split("\r\n\r\n", 1)
        header_section = parts[0]
        body = parts[1] if len(parts) > 1 else ""

        lines = header_section.split("\r\n")
        request_line = lines[0]

        # 요청 라인 파싱: "GET /path?key=value HTTP/1.1"
        method, url, _ = request_line.split(" ", 2)

        # URL에서 경로와 쿼리 파라미터 분리
        path = url
        query_params = {}
        if "?" in url:
            path, qs = url.split("?", 1)
            query_params = {k: v[0] for k, v in parse_qs(qs).items()}

        # 헤더 파싱
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value

        # JSON 바디 파싱
        json_body = None
        if body and headers.get("Content-Type") == "application/json":
            try:
                json_body = json.loads(body)
            except json.JSONDecodeError:
                pass

        return ParsedRequest(method, path, query_params, headers, body, json_body)

    # ─── 파싱 테스트 ───

    print("  ─── GET 요청 파싱 ───")
    get_raw = "GET /students?grade=3&sort=name HTTP/1.1\r\nHost: localhost\r\nAccept: application/json\r\n\r\n"
    get_parsed = parse_request(get_raw)
    print(f"    메서드: {get_parsed.method}")
    print(f"    경로: {get_parsed.path}")
    print(f"    쿼리: {get_parsed.query_params}")
    print(f"    헤더: {get_parsed.headers}")
    print()

    print("  ─── POST 요청 파싱 ───")
    post_raw = (
        'POST /students HTTP/1.1\r\n'
        'Host: localhost\r\n'
        'Content-Type: application/json\r\n'
        '\r\n'
        '{"name": "민수", "grade": 3}'
    )
    post_parsed = parse_request(post_raw)
    print(f"    메서드: {post_parsed.method}")
    print(f"    경로: {post_parsed.path}")
    print(f"    JSON 바디: {post_parsed.json_body}")
    print()

    # ─── URL 디코딩 ───

    print("  ─── URL 디코딩 ───")
    encoded = "%ED%95%9C%EA%B8%80%20%ED%85%8C%EC%8A%A4%ED%8A%B8"
    decoded = unquote(encoded)
    print(f"    인코딩: {encoded}")
    print(f"    디코딩: {decoded}")
    print()


# =========================================================================
#
#   레슨 7 — 미들웨어 개념
#
# =========================================================================

def lesson7_middleware():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 7 : 미들웨어 개념               │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ 미들웨어란?
    # ─────────────────────────────────────────────────────────────────────
    #
    #   요청이 핸들러에 도달하기 전/후에 실행되는 코드입니다.
    #
    #   비유: 공항 보안 검색대
    #     → 승객(요청)이 게이트(핸들러)에 가기 전에 보안 검색(미들웨어)
    #     → 여러 검색대를 순서대로 통과! (체인)
    #
    #   용도:
    #   - 로깅 (요청/응답 기록)
    #   - 인증 (로그인 확인)
    #   - CORS (교차 출처 허용)
    #   - 에러 핸들링
    #   - 응답 압축
    #

    # ─── 미들웨어 체인 구현 ───

    class MiddlewareChain:
        def __init__(self):
            self.middlewares: list[Callable] = []

        def add(self, middleware: Callable):
            self.middlewares.append(middleware)

        def process(self, request: dict, handler: Callable) -> dict:
            """미들웨어 체인을 실행합니다."""
            # 체인을 역순으로 감싸기 (양파 껍질처럼)
            current = handler
            for mw in reversed(self.middlewares):
                current = self._wrap(mw, current)
            return current(request)

        def _wrap(self, middleware, next_handler):
            return lambda req: middleware(req, next_handler)

    # ─── 미들웨어 구현 ───

    def logging_middleware(request, next_handler):
        """요청/응답을 로깅합니다."""
        print(f"    [LOG] → 요청: {request['method']} {request['path']}")
        response = next_handler(request)
        print(f"    [LOG] ← 응답: {response['status']}")
        return response

    def auth_middleware(request, next_handler):
        """인증을 확인합니다."""
        token = request.get("headers", {}).get("Authorization")
        if request["path"].startswith("/admin") and token != "Bearer secret123":
            print(f"    [AUTH] 인증 실패!")
            return {"status": 401, "body": {"error": "Unauthorized"}}
        print(f"    [AUTH] 인증 통과")
        return next_handler(request)

    def timing_middleware(request, next_handler):
        """처리 시간을 측정합니다."""
        start = time.perf_counter()
        response = next_handler(request)
        elapsed = time.perf_counter() - start
        response["headers"] = response.get("headers", {})
        response["headers"]["X-Response-Time"] = f"{elapsed:.4f}s"
        print(f"    [TIMER] 처리 시간: {elapsed:.4f}초")
        return response

    # ─── 핸들러 ───

    def my_handler(request):
        return {"status": 200, "body": {"message": "OK"}}

    # ─── 미들웨어 체인 실행 ───

    chain = MiddlewareChain()
    chain.add(timing_middleware)
    chain.add(logging_middleware)
    chain.add(auth_middleware)

    print("  ─── 일반 요청 (미들웨어 3개 통과) ───")
    result = chain.process(
        {"method": "GET", "path": "/students", "headers": {}},
        my_handler
    )
    print(f"    결과: {result}")
    print()

    print("  ─── 관리자 요청 (인증 실패) ───")
    result = chain.process(
        {"method": "GET", "path": "/admin/users", "headers": {}},
        my_handler
    )
    print(f"    결과: {result}")
    print()

    print("  ─── 관리자 요청 (인증 성공) ───")
    result = chain.process(
        {"method": "GET", "path": "/admin/users",
         "headers": {"Authorization": "Bearer secret123"}},
        my_handler
    )
    print(f"    결과: {result}")
    print()


# =========================================================================
#
#   레슨 8 — 세션과 쿠키 개념
#
# =========================================================================

def lesson8_session_cookie():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 8 : 세션과 쿠키 개념             │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ HTTP는 상태가 없다 (Stateless)
    # ─────────────────────────────────────────────────────────────────────
    #
    #   HTTP는 매 요청이 독립적입니다.
    #   서버는 "이 요청을 보낸 사람이 아까 그 사람인지" 모릅니다!
    #
    #   비유: 금붕어 기억력
    #     → 매번 "저 누구세요?" 하는 서버
    #     → 그래서 "이름표(쿠키)"를 달아줌!
    #
    #   쿠키(Cookie):
    #   → 클라이언트(브라우저)에 저장되는 작은 데이터
    #   → 매 요청마다 서버에 자동으로 전송됨
    #
    #   세션(Session):
    #   → 서버에 저장되는 사용자 데이터
    #   → 세션 ID(쿠키)로 사용자를 식별
    #

    # ─── 세션 저장소 구현 ───

    class SessionStore:
        """서버 측 세션 저장소."""
        def __init__(self):
            self.sessions: dict[str, dict] = {}

        def create_session(self, user_data: dict) -> str:
            """새 세션을 만들고 세션 ID를 반환합니다."""
            session_id = str(uuid.uuid4())[:8]  # 짧은 ID
            self.sessions[session_id] = {
                "data": user_data,
                "created_at": time.time(),
            }
            return session_id

        def get_session(self, session_id: str) -> dict | None:
            """세션 ID로 세션 데이터를 조회합니다."""
            session = self.sessions.get(session_id)
            if session is None:
                return None
            return session["data"]

        def destroy_session(self, session_id: str) -> bool:
            """세션을 삭제합니다 (로그아웃)."""
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False

    # ─── 세션 기반 인증 시뮬레이션 ───

    store = SessionStore()

    print("  ─── 세션 기반 인증 시뮬레이션 ───")
    print()

    # 1. 로그인 → 세션 생성
    print("  1. 로그인:")
    session_id = store.create_session({"user": "민수", "role": "student"})
    print(f"     세션 ID (쿠키에 저장): {session_id}")
    print(f"     Set-Cookie: session_id={session_id}")
    print()

    # 2. 이후 요청 → 세션 확인
    print("  2. 이후 요청 (쿠키에서 세션 ID 전송):")
    user_data = store.get_session(session_id)
    if user_data:
        print(f"     Cookie: session_id={session_id}")
        print(f"     서버에서 세션 확인 → 사용자: {user_data}")
    print()

    # 3. 로그아웃 → 세션 삭제
    print("  3. 로그아웃:")
    store.destroy_session(session_id)
    user_data = store.get_session(session_id)
    print(f"     세션 삭제 후 조회: {user_data}")
    print()

    # ─── 보안 고려사항 ───

    print("  ■ 세션/쿠키 보안 고려사항:")
    print("    1. HttpOnly: JavaScript에서 쿠키 접근 차단 (XSS 방지)")
    print("    2. Secure: HTTPS에서만 쿠키 전송")
    print("    3. SameSite: 다른 사이트에서 쿠키 전송 제한 (CSRF 방지)")
    print("    4. 세션 만료: 일정 시간 후 자동 삭제")
    print("    5. 세션 ID는 예측 불가능해야 함 (UUID 등 사용)")
    print()


# =========================================================================
#
#   레슨 9 — 실전: 미니 웹 프레임워크 만들기
#
# =========================================================================

def lesson9_mini_framework():
    print("┌──────────────────────────────────────┐")
    print("│  레슨 9 : 미니 웹 프레임워크            │")
    print("└──────────────────────────────────────┘")
    print()

    # ─────────────────────────────────────────────────────────────────────
    # ■ Flask 스타일 미니 프레임워크
    # ─────────────────────────────────────────────────────────────────────
    #
    #   지금까지 배운 것을 모두 합쳐서 Flask와 비슷한 프레임워크를 만듭니다!
    #
    #   기능:
    #   - 데코레이터로 라우트 등록 (@app.route)
    #   - GET/POST 지원
    #   - 경로 파라미터 (<name>)
    #   - JSON 응답
    #   - 미들웨어 지원
    #

    class MiniFlask:
        def __init__(self, name: str):
            self.name = name
            self.routes: dict[tuple[str, str], Callable] = {}
            self.middlewares: list[Callable] = []
            self.db: dict[str, list] = {}  # 간단한 인메모리 DB

        def route(self, path: str, methods: list[str] = None):
            """데코레이터로 라우트를 등록합니다."""
            methods = methods or ["GET"]
            def decorator(func):
                for method in methods:
                    self.routes[(method, path)] = func
                return func
            return decorator

        def use(self, middleware: Callable):
            """미들웨어를 등록합니다."""
            self.middlewares.append(middleware)

        def _match_route(self, method: str, path: str):
            """경로 패턴 매칭."""
            for (route_method, pattern), handler in self.routes.items():
                if route_method != method:
                    continue
                regex = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern)
                match = re.fullmatch(regex, path)
                if match:
                    return handler, match.groupdict()
            return None, {}

        def handle_request(self, method: str, path: str, body: dict = None) -> dict:
            """요청을 처리합니다."""
            # 쿼리 스트링 분리
            query = {}
            if "?" in path:
                path, qs = path.split("?", 1)
                query = {k: v[0] for k, v in parse_qs(qs).items()}

            request = {
                "method": method,
                "path": path,
                "query": query,
                "body": body or {},
            }

            # 핸들러 찾기
            handler, path_params = self._match_route(method, path)
            if handler is None:
                return {"status": 404, "body": {"error": "Not Found"}}

            request["path_params"] = path_params

            # 미들웨어 체인 + 핸들러 실행
            def run_handler(req):
                return handler(**req.get("path_params", {}),
                               request=req)

            current = run_handler
            for mw in reversed(self.middlewares):
                prev = current
                current = lambda req, _mw=mw, _prev=prev: _mw(req, _prev)

            return current(request)

    # ─── 앱 생성 ───

    app = MiniFlask("학생관리")

    # 인메모리 데이터
    students = [
        {"id": 1, "name": "민수", "grade": 3, "score": 95},
        {"id": 2, "name": "지유", "grade": 4, "score": 88},
        {"id": 3, "name": "서연", "grade": 3, "score": 78},
    ]
    next_id = 4

    # ─── 라우트 등록 ───

    @app.route("/")
    def index(request):
        return {"status": 200, "body": {"message": "학생관리 API v1.0"}}

    @app.route("/students")
    def get_students(request):
        grade = request.get("query", {}).get("grade")
        result = students
        if grade:
            result = [s for s in result if s["grade"] == int(grade)]
        return {"status": 200, "body": {"students": result, "count": len(result)}}

    @app.route("/students/<name>")
    def get_student(name, request):
        student = next((s for s in students if s["name"] == name), None)
        if student:
            return {"status": 200, "body": student}
        return {"status": 404, "body": {"error": f"'{name}' 없음"}}

    @app.route("/students", methods=["POST"])
    def create_student(request):
        nonlocal next_id
        body = request.get("body", {})
        new_student = {"id": next_id, **body}
        students.append(new_student)
        next_id += 1
        return {"status": 201, "body": new_student}

    # ─── 미들웨어 등록 ───

    def log_middleware(request, next_handler):
        print(f"    [LOG] {request['method']} {request['path']}")
        return next_handler(request)

    app.use(log_middleware)

    # ─── 프레임워크 테스트 ───

    print("  ─── MiniFlask 프레임워크 테스트 ───")
    print()

    test_cases = [
        ("GET", "/", None, "홈페이지"),
        ("GET", "/students", None, "전체 목록"),
        ("GET", "/students?grade=3", None, "3학년 필터"),
        ("GET", "/students/민수", None, "학생 조회"),
        ("POST", "/students", {"name": "하준", "grade": 5, "score": 82}, "학생 추가"),
        ("GET", "/students", None, "추가 후 목록"),
        ("GET", "/unknown", None, "없는 경로"),
    ]

    for method, path, body, desc in test_cases:
        result = app.handle_request(method, path, body)
        print(f"    [{desc}] {method} {path} → [{result['status']}] {result['body']}")
    print()

    print("  ★ 이 미니 프레임워크에서 사용된 개념:")
    print("    - 라우팅 (URL → 함수 매핑)")
    print("    - 데코레이터 (@app.route)")
    print("    - 경로 파라미터 (<name>)")
    print("    - 쿼리 스트링 파싱")
    print("    - 미들웨어 체인")
    print("    - JSON 요청/응답")
    print("    - REST API 패턴 (CRUD)")
    print()


# ─────────────────────────────────────────────────────────────────────────
# ■ 메인 실행
# ─────────────────────────────────────────────────────────────────────────

def main():
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print("  파이썬 학습 13단계: 웹 기초")
    print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
    print()

    lesson1_http_protocol()
    lesson2_socket_http()
    lesson3_routing()
    lesson4_template_engine()
    lesson5_rest_api()
    lesson6_request_parsing()
    lesson7_middleware()
    lesson8_session_cookie()
    lesson9_mini_framework()

    print("=" * 60)
    print("  13단계 완료! 웹의 기초 원리를 모두 배웠습니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()
