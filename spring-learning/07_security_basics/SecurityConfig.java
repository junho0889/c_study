/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 07단계: Spring Security 설정 (SecurityConfig.java)
  ─ SecurityFilterChain, PasswordEncoder, 인증/인가 설정 ─

  Spring Security는 애플리케이션의 "보안 경비원"입니다.
  누가 들어올 수 있는지, 어디까지 갈 수 있는지 관리합니다.

  ■ 이 파일은 개념 설명용입니다 (컴파일하려면 Spring Boot 프로젝트 필요)

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.springframework.context.annotation.Bean;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
// import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
// import org.springframework.security.crypto.password.PasswordEncoder;
// import org.springframework.security.web.SecurityFilterChain;


/*
┌─────────────────────────────────────────────────────────────┐
│  Spring Security의 전체 흐름                                │
│                                                             │
│  비유: 학교 출입 보안 시스템!                                │
│                                                             │
│  [학생] → [정문 경비(필터)] → [학생증 확인(인증)]           │
│        → [출입 가능 구역 확인(인가)] → [교실(컨트롤러)]     │
│                                                             │
│  HTTP 요청이 들어오면 Spring Security의 필터 체인을 통과:   │
│                                                             │
│  요청 → 필터1 → 필터2 → ... → 필터N → 컨트롤러            │
│        (CORS)  (CSRF)  ... (인증필터)                        │
│                                                             │
│  각 필터가 순서대로 요청을 검사합니다.                       │
│  하나라도 실패하면 → 401 또는 403 에러!                     │
└─────────────────────────────────────────────────────────────┘
*/

// @Configuration
// @EnableMethodSecurity  // @PreAuthorize 등 메서드 수준 보안 활성화
public class SecurityConfig {

    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  SecurityFilterChain = 보안 규칙 정의                 │
     * │                                                       │
     * │  "어떤 URL은 누구나 접근 가능하고,                    │
     * │   어떤 URL은 로그인한 사람만 접근 가능하고,            │
     * │   어떤 URL은 관리자만 접근 가능하다"                   │
     * │                                                       │
     * │  비유: 놀이공원 입장 규칙!                             │
     * │  - 입구: 누구나 OK                                    │
     * │  - 일반 놀이기구: 입장권 필요                          │
     * │  - VIP 라운지: VIP 입장권 필요                        │
     * └───────────────────────────────────────────────────────┘
     */

    // @Bean
    // public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    //     http
    //         // ─── CSRF 설정 ───
    //         // REST API는 보통 CSRF를 비활성화합니다
    //         // (브라우저 폼이 아니라 토큰 기반이니까)
    //         .csrf(csrf -> csrf.disable())
    //
    //         // ─── URL별 접근 권한 설정 ───
    //         .authorizeHttpRequests(auth -> auth
    //             // 누구나 접근 가능 (로그인 불필요)
    //             .requestMatchers("/", "/login", "/register").permitAll()
    //             .requestMatchers("/api/public/**").permitAll()
    //
    //             // STUDENT 또는 TEACHER 역할만 접근 가능
    //             .requestMatchers("/api/students/**").hasAnyRole("STUDENT", "TEACHER")
    //
    //             // TEACHER 역할만 접근 가능
    //             .requestMatchers("/api/scores/**").hasRole("TEACHER")
    //
    //             // ADMIN 역할만 접근 가능
    //             .requestMatchers("/api/admin/**").hasRole("ADMIN")
    //
    //             // 나머지는 인증 필요
    //             .anyRequest().authenticated()
    //         )
    //
    //         // ─── 로그인 방식 설정 ───
    //         .httpBasic(basic -> {})  // HTTP Basic 인증
    //         // 또는 .formLogin(form -> {})  // 폼 로그인
    //         ;
    //
    //     return http.build();
    // }

    /*
     * ┌───────────────────────────────────────────────────────┐
     * │  PasswordEncoder = 비밀번호 암호화                     │
     * │                                                       │
     * │  비밀번호를 그대로 DB에 저장하면 매우 위험!            │
     * │  해킹당하면 모든 비밀번호가 노출됩니다.               │
     * │                                                       │
     * │  BCrypt는 비밀번호를 암호화하는 알고리즘입니다.        │
     * │                                                       │
     * │  "1234" → "$2a$10$xKz3..."  (다시 원래로 못 돌림!)    │
     * │                                                       │
     * │  비유: 금고에 넣으면 꺼낼 수 없는 "단방향 잠금 장치"  │
     * │  같은 비밀번호를 넣으면 같은 결과가 나오므로           │
     * │  비교는 가능하지만, 원본을 알아낼 수는 없습니다!       │
     * └───────────────────────────────────────────────────────┘
     */

    // @Bean
    // public PasswordEncoder passwordEncoder() {
    //     return new BCryptPasswordEncoder();
    //     // 사용법:
    //     // String encoded = passwordEncoder.encode("1234");
    //     // boolean matches = passwordEncoder.matches("1234", encoded);
    // }


    // ─────────────────────────────────────────────────────────
    // 개념 설명용 main 메서드
    // ─────────────────────────────────────────────────────────

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 07단계 : Spring Security 설정");
        System.out.println("============================================================");
        System.out.println();

        lesson1SecurityFlow();
        lesson2UrlAuthorization();
        lesson3PasswordEncoder();
    }

    public static void lesson1SecurityFlow() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : Spring Security 동작 흐름          │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  요청이 들어오면 이런 순서로 처리됩니다:");
        System.out.println();
        System.out.println("  1. 요청 도착");
        System.out.println("  2. Security Filter Chain 통과");
        System.out.println("     ├─ CORS 필터: 다른 도메인에서 온 요청 허용?");
        System.out.println("     ├─ CSRF 필터: 위조 요청 방지");
        System.out.println("     ├─ 인증 필터: 로그인 정보 확인");
        System.out.println("     └─ 인가 필터: 접근 권한 확인");
        System.out.println("  3. 모든 필터 통과 → 컨트롤러 실행");
        System.out.println("  4. 필터 실패 → 401(인증실패) 또는 403(권한없음)");
        System.out.println();
    }

    public static void lesson2UrlAuthorization() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : URL별 접근 권한                    │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  permitAll()    → 누구나 OK (로그인 페이지, 공개 API)");
        System.out.println("  authenticated()→ 로그인한 사람만");
        System.out.println("  hasRole(\"X\")   → X 역할이 있는 사람만");
        System.out.println("  hasAnyRole()   → 여러 역할 중 하나라도 있으면 OK");
        System.out.println();
        System.out.println("  예시 시나리오:");
        System.out.println("    GET /             → permitAll (홈페이지)");
        System.out.println("    GET /api/students → STUDENT or TEACHER");
        System.out.println("    POST /api/scores  → TEACHER only");
        System.out.println("    GET /api/admin    → ADMIN only");
        System.out.println();
        System.out.println("  비유: 놀이공원의 구역별 입장 제한과 같습니다!");
        System.out.println();
    }

    public static void lesson3PasswordEncoder() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : 비밀번호 암호화                    │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  절대 해서는 안 되는 것:");
        System.out.println("    비밀번호를 그대로 DB에 저장! (password = \"1234\")");
        System.out.println();
        System.out.println("  올바른 방법:");
        System.out.println("    BCrypt로 암호화 후 저장!");
        System.out.println("    \"1234\" → encode() → \"$2a$10$xKz3R...\"");
        System.out.println();
        System.out.println("  로그인 시 비교:");
        System.out.println("    사용자 입력: \"1234\"");
        System.out.println("    DB 저장값:   \"$2a$10$xKz3R...\"");
        System.out.println("    matches(\"1234\", \"$2a$10$...\") → true!");
        System.out.println();
        System.out.println("  BCrypt의 특징:");
        System.out.println("    - 같은 비밀번호도 매번 다른 암호문이 생성됨 (salt)");
        System.out.println("    - 원본 비밀번호를 역추적할 수 없음 (단방향)");
        System.out.println("    - 의도적으로 느리게 만들어 무차별 대입 공격 방지");
        System.out.println();
    }
}
