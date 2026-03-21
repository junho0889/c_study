/*
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

  Spring 학습 07단계: Spring Security 추가 설명
  ─ UserDetailsService, @PreAuthorize, 인증 흐름 상세 ─

  SecurityConfig.java와 함께 보면 좋습니다.

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
*/

// import org.springframework.security.core.userdetails.UserDetailsService;
// import org.springframework.security.core.userdetails.UserDetails;
// import org.springframework.security.core.userdetails.User;
// import org.springframework.security.access.prepost.PreAuthorize;


/*
┌─────────────────────────────────────────────────────────────┐
│  UserDetailsService = "사용자 정보를 어디서 가져올지" 알려주기│
│                                                             │
│  비유: 경비원이 출입자 명단을 어디서 확인하는지!             │
│  - 종이 명단(InMemory) → 개발/테스트용                      │
│  - 컴퓨터 데이터베이스(DB) → 실제 운영용                    │
│  - 외부 시스템(LDAP, OAuth) → 회사 시스템 연동              │
└─────────────────────────────────────────────────────────────┘
*/

// @Service
// public class CustomUserDetailsService implements UserDetailsService {
//
//     // @Autowired
//     // private UserRepository userRepository;
//
//     // @Override
//     // public UserDetails loadUserByUsername(String username) {
//     //     // DB에서 사용자 조회
//     //     UserEntity user = userRepository.findByUsername(username)
//     //         .orElseThrow(() -> new UsernameNotFoundException("사용자 없음: " + username));
//     //
//     //     // Spring Security가 이해하는 UserDetails 객체로 변환
//     //     return User.builder()
//     //         .username(user.getUsername())
//     //         .password(user.getPassword())  // 이미 BCrypt로 암호화된 비밀번호
//     //         .roles(user.getRole())          // "STUDENT", "TEACHER" 등
//     //         .build();
//     // }
// }


/*
┌─────────────────────────────────────────────────────────────┐
│  @PreAuthorize = 메서드 수준 보안                            │
│                                                             │
│  URL 수준이 아니라 메서드 하나하나에 권한을 지정!            │
│                                                             │
│  비유:                                                      │
│  SecurityConfig = 건물 출입 규칙 (층별 제한)                │
│  @PreAuthorize  = 방별 출입 규칙 (더 세밀한 제어)           │
└─────────────────────────────────────────────────────────────┘
*/

// @RestController
// @RequestMapping("/api/students")
// public class StudentController {
//
//     // 누구나 조회 가능
//     // @GetMapping
//     // public List<Student> getAllStudents() { ... }
//
//     // TEACHER 역할만 성적 수정 가능
//     // @PreAuthorize("hasRole('TEACHER')")
//     // @PatchMapping("/{id}/score")
//     // public Student updateScore(@PathVariable Long id, @RequestBody int score) { ... }
//
//     // 본인이거나 ADMIN만 개인정보 조회 가능
//     // @PreAuthorize("hasRole('ADMIN') or #username == authentication.name")
//     // @GetMapping("/{username}/profile")
//     // public StudentProfile getProfile(@PathVariable String username) { ... }
//
//     // ADMIN만 학생 삭제 가능
//     // @PreAuthorize("hasRole('ADMIN')")
//     // @DeleteMapping("/{id}")
//     // public void deleteStudent(@PathVariable Long id) { ... }
// }


public class explanation {

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  Spring 07단계 : Spring Security 추가 설명");
        System.out.println("============================================================");
        System.out.println();

        lesson1UserDetailsService();
        lesson2PreAuthorize();
        lesson3AuthenticationFlow();
    }

    public static void lesson1UserDetailsService() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 1 : UserDetailsService                │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  Spring Security가 로그인을 처리할 때:");
        System.out.println("    1. 사용자가 아이디/비밀번호 입력");
        System.out.println("    2. Spring이 UserDetailsService.loadUserByUsername() 호출");
        System.out.println("    3. DB에서 사용자 정보 조회");
        System.out.println("    4. 비밀번호 비교 (PasswordEncoder.matches())");
        System.out.println("    5. 일치하면 인증 성공! 세션 또는 토큰 발급");
        System.out.println();
        System.out.println("  우리가 할 일:");
        System.out.println("    UserDetailsService를 구현해서 '어디서 사용자를 찾을지' 알려주기!");
        System.out.println("    나머지(비밀번호 비교, 세션 관리 등)는 Spring이 알아서 합니다.");
        System.out.println();
    }

    public static void lesson2PreAuthorize() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 2 : @PreAuthorize (메서드 보안)        │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  @PreAuthorize 표현식 예시:");
        System.out.println();
        System.out.println("  hasRole('TEACHER')");
        System.out.println("    → TEACHER 역할 필요");
        System.out.println();
        System.out.println("  hasAnyRole('STUDENT', 'TEACHER')");
        System.out.println("    → 둘 중 하나면 OK");
        System.out.println();
        System.out.println("  hasRole('ADMIN') or #id == authentication.principal.id");
        System.out.println("    → 관리자이거나 본인이면 OK");
        System.out.println();
        System.out.println("  @PreAuthorize(\"isAuthenticated()\")");
        System.out.println("    → 로그인만 하면 누구나 OK");
        System.out.println();
        System.out.println("  비유: 문마다 다른 잠금장치를 거는 것!");
        System.out.println("  교실 문 = 학생이면 OK, 교무실 문 = 선생님만 OK");
        System.out.println();
    }

    public static void lesson3AuthenticationFlow() {
        System.out.println("┌──────────────────────────────────────────────┐");
        System.out.println("│  레슨 3 : 인증 전체 흐름 정리                │");
        System.out.println("└──────────────────────────────────────────────┘");
        System.out.println();
        System.out.println("  1. 클라이언트 → POST /login {username, password}");
        System.out.println("  2. AuthenticationFilter가 요청 가로채기");
        System.out.println("  3. AuthenticationManager에게 인증 위임");
        System.out.println("  4. UserDetailsService.loadUserByUsername() 호출");
        System.out.println("  5. DB에서 사용자 조회");
        System.out.println("  6. PasswordEncoder.matches()로 비밀번호 비교");
        System.out.println("  7. 인증 성공 → SecurityContext에 인증 정보 저장");
        System.out.println("  8. 이후 요청마다 SecurityContext에서 인증 확인");
        System.out.println();
        System.out.println("  핵심 컴포넌트:");
        System.out.println("    AuthenticationManager  → 인증 과정 총괄");
        System.out.println("    UserDetailsService     → 사용자 정보 조회");
        System.out.println("    PasswordEncoder        → 비밀번호 암호화/비교");
        System.out.println("    SecurityContext         → 현재 인증 정보 보관");
        System.out.println("    SecurityFilterChain    → 보안 필터 규칙 정의");
        System.out.println();
    }
}
