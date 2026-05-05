// ============================================================================
// 미니 프로그래밍 언어 인터프리터 (Mini Language Interpreter)
// ============================================================================
// C/C++로 만든 유명한 것들: GCC, Clang, V8, Python 인터프리터
// 왜 C++? 컴파일러는 빠른 속도와 직접 메모리 제어가 필요합니다!
//
//  인터프리터 파이프라인:
//  ┌──────────┐   ┌────────┐   ┌────────┐   ┌──────────┐
//  │ 소스코드  │──>│ 렉서   │──>│ 파서   │──>│ 인터프리터│
//  │ (문자열)  │   │(토큰화) │   │(AST생성)│   │  (실행)   │
//  └──────────┘   └────────┘   └────────┘   └──────────┘
//
//  "let x = 10 + 20" → [LET][x][=][10][+][20] → AST → x=30
// ============================================================================

#include <iostream>
#include <string>
#include <vector>      // C#의 List<T>와 같습니다
#include <memory>      // unique_ptr<ASTNode>는 C#에서 ASTNode 참조변수와 비슷하지만, 소유권이 명확합니다
#include <variant>     // variant는 C#의 object와 비슷하게 여러 타입을 담을 수 있습니다
#include <unordered_map> // C#의 Dictionary<K,V>
#include <sstream>
#include <cmath>

// ============================================================================
// 1단계: 토큰 - Lexer는 C#의 Roslyn 컴파일러에서 SyntaxToken을 만드는 부분과 같습니다
// ============================================================================
enum class TokenType {
    NUMBER, STRING, IDENTIFIER,           // 값 토큰
    PLUS, MINUS, STAR, SLASH, ASSIGN,     // 연산자
    LESS, GREATER, LESS_EQUAL, GREATER_EQUAL, EQUAL_EQUAL, NOT_EQUAL,  // 비교
    LPAREN, RPAREN,                       // 괄호
    LET, PRINT, IF, ELSE, WHILE, END, AND, OR, NOT,  // 키워드
    NEWLINE, END_OF_FILE
};

// 토큰 구조체 - C#에서 class Token { TokenType Type; string Value; int Line; }
struct Token {
    TokenType type;
    std::string value;
    int line;
    Token(TokenType t, const std::string& v, int l) : type(t), value(v), line(l) {}
};

// ============================================================================
// 2단계: 렉서 (Lexer) - 소스코드를 토큰으로 쪼개는 기계
// ============================================================================
//  "let x = 10" → [LET] [x] [=] [10]
class Lexer {
    std::string src_;
    size_t pos_;
    int line_;

    char cur() const { return pos_ < src_.size() ? src_[pos_] : '\0'; }
    char peek() const { return pos_+1 < src_.size() ? src_[pos_+1] : '\0'; }
    void adv() { if (cur() == '\n') line_++; pos_++; }

    // 공백 건너뛰기 (줄바꿈은 보존! 문장 구분자이니까요)
    void skipWS() { while (pos_ < src_.size() && (cur()==' '||cur()=='\t'||cur()=='\r')) adv(); }
    void skipComment() { if (cur()=='#') while (pos_<src_.size()&&cur()!='\n') adv(); }

    // 숫자 읽기 - C#의 double.Parse()와 비슷
    Token readNum() {
        std::string n; int sl=line_;
        while (pos_<src_.size()&&(std::isdigit(cur())||cur()=='.')) { n+=cur(); adv(); }
        return {TokenType::NUMBER, n, sl};
    }
    // 문자열 읽기 - "" 사이의 내용
    Token readStr() {
        int sl=line_; adv(); // 시작 " 건너뛰기
        std::string s;
        while (pos_<src_.size()&&cur()!='"') {
            if (cur()=='\\') { adv();
                switch(cur()) { case 'n': s+='\n'; break; case 't': s+='\t'; break; default: s+=cur(); }
            } else s+=cur();
            adv();
        }
        if (pos_<src_.size()) adv(); // 끝 " 건너뛰기
        return {TokenType::STRING, s, sl};
    }
    // 식별자/키워드 읽기
    Token readId() {
        std::string id; int sl=line_;
        while (pos_<src_.size()&&(std::isalnum(cur())||cur()=='_')) { id+=cur(); adv(); }
        // 키워드 확인 - C#에서도 예약어를 별도 처리하죠!
        if (id=="let") return {TokenType::LET,id,sl};
        if (id=="print") return {TokenType::PRINT,id,sl};
        if (id=="if") return {TokenType::IF,id,sl};
        if (id=="else") return {TokenType::ELSE,id,sl};
        if (id=="while") return {TokenType::WHILE,id,sl};
        if (id=="end") return {TokenType::END,id,sl};
        if (id=="and") return {TokenType::AND,id,sl};
        if (id=="or") return {TokenType::OR,id,sl};
        if (id=="not") return {TokenType::NOT,id,sl};
        return {TokenType::IDENTIFIER, id, sl};
    }

public:
    Lexer(const std::string& src) : src_(src), pos_(0), line_(1) {}

    // 토큰화 - C#에서 List<Token> Tokenize()와 같습니다
    std::vector<Token> tokenize() {
        std::vector<Token> toks;
        while (pos_ < src_.size()) {
            skipWS(); skipComment();
            if (pos_ >= src_.size()) break;
            char c = cur();
            if (c=='\n') {
                if (!toks.empty()&&toks.back().type!=TokenType::NEWLINE)
                    toks.push_back({TokenType::NEWLINE,"\\n",line_});
                adv(); continue;
            }
            if (std::isdigit(c)) { toks.push_back(readNum()); continue; }
            if (c=='"') { toks.push_back(readStr()); continue; }
            if (std::isalpha(c)||c=='_') { toks.push_back(readId()); continue; }

            // 연산자와 기호 - C#에서도 switch로 처리합니다!
            auto two = [&](TokenType t, const std::string& v) { toks.push_back({t,v,line_}); adv(); adv(); };
            auto one = [&](TokenType t, const std::string& v) { toks.push_back({t,v,line_}); adv(); };
            switch(c) {
                case '+': one(TokenType::PLUS,"+"); break;
                case '-': one(TokenType::MINUS,"-"); break;
                case '*': one(TokenType::STAR,"*"); break;
                case '/': one(TokenType::SLASH,"/"); break;
                case '(': one(TokenType::LPAREN,"("); break;
                case ')': one(TokenType::RPAREN,")"); break;
                case '=': peek()=='=' ? two(TokenType::EQUAL_EQUAL,"==") : one(TokenType::ASSIGN,"="); break;
                case '<': peek()=='=' ? two(TokenType::LESS_EQUAL,"<=") : one(TokenType::LESS,"<"); break;
                case '>': peek()=='=' ? two(TokenType::GREATER_EQUAL,">=") : one(TokenType::GREATER,">"); break;
                case '!': peek()=='=' ? two(TokenType::NOT_EQUAL,"!=") : (std::cerr<<"[오류] "<<line_<<"줄: '!'\n", adv()); break;
                default: std::cerr<<"[오류] "<<line_<<"줄: '"<<c<<"'\n"; adv();
            }
        }
        if (!toks.empty()&&toks.back().type!=TokenType::NEWLINE)
            toks.push_back({TokenType::NEWLINE,"\\n",line_});
        toks.push_back({TokenType::END_OF_FILE,"",line_});
        return toks;
    }
};

// ============================================================================
// 3단계: AST 노드 - AST는 C#의 Roslyn SyntaxTree와 같은 개념입니다
// ============================================================================
//  "10 + 20 * 3" 의 AST:
//        [+]
//       /   \
//     [10]  [*]
//          /   \
//        [20]  [3]

// 값 타입 - variant는 C#의 object와 비슷합니다
using Value = std::variant<double, std::string, bool>;

std::string valStr(const Value& v) {
    return std::visit([](auto&& a) -> std::string {
        using T = std::decay_t<decltype(a)>;
        if constexpr (std::is_same_v<T,double>) {
            if (a==static_cast<int>(a)) return std::to_string(static_cast<int>(a));
            std::ostringstream o; o<<a; return o.str();
        } else if constexpr (std::is_same_v<T,std::string>) return a;
        else return a ? "true" : "false";
    }, v);
}
double valNum(const Value& v) {
    if (auto* d=std::get_if<double>(&v)) return *d;
    if (auto* b=std::get_if<bool>(&v)) return *b ? 1.0 : 0.0;
    return 0.0;
}
bool truthy(const Value& v) {
    if (auto* d=std::get_if<double>(&v)) return *d!=0.0;
    if (auto* s=std::get_if<std::string>(&v)) return !s->empty();
    if (auto* b=std::get_if<bool>(&v)) return *b;
    return false;
}

// AST 기본 클래스 - C#의 abstract class ASTNode
struct ASTNode { int line; ASTNode(int l):line(l){} virtual ~ASTNode()=default; };
using NodePtr = std::unique_ptr<ASTNode>;  // unique_ptr = C#의 참조변수 + 소유권

// --- AST 노드 종류들 ---
struct NumberLit : ASTNode { double value; NumberLit(double v,int l):ASTNode(l),value(v){} };
struct StringLit : ASTNode { std::string value; StringLit(const std::string& v,int l):ASTNode(l),value(v){} };
struct BinaryOp : ASTNode {
    NodePtr left; std::string op; NodePtr right;
    BinaryOp(NodePtr l,const std::string& o,NodePtr r,int ln):ASTNode(ln),left(std::move(l)),op(o),right(std::move(r)){}
};
struct UnaryOp : ASTNode {
    std::string op; NodePtr operand;
    UnaryOp(const std::string& o,NodePtr e,int l):ASTNode(l),op(o),operand(std::move(e)){}
};
struct VarDecl : ASTNode {
    std::string name; NodePtr init;
    VarDecl(const std::string& n,NodePtr i,int l):ASTNode(l),name(n),init(std::move(i)){}
};
struct VarAccess : ASTNode { std::string name; VarAccess(const std::string& n,int l):ASTNode(l),name(n){} };
struct VarAssign : ASTNode {
    std::string name; NodePtr value;
    VarAssign(const std::string& n,NodePtr v,int l):ASTNode(l),name(n),value(std::move(v)){}
};
struct PrintStmt : ASTNode { NodePtr expr; PrintStmt(NodePtr e,int l):ASTNode(l),expr(std::move(e)){} };
struct IfStmt : ASTNode {
    NodePtr cond; std::vector<NodePtr> thenB, elseB;
    IfStmt(NodePtr c,std::vector<NodePtr> t,std::vector<NodePtr> e,int l)
        :ASTNode(l),cond(std::move(c)),thenB(std::move(t)),elseB(std::move(e)){}
};
struct WhileStmt : ASTNode {
    NodePtr cond; std::vector<NodePtr> body;
    WhileStmt(NodePtr c,std::vector<NodePtr> b,int l):ASTNode(l),cond(std::move(c)),body(std::move(b)){}
};
struct Block : ASTNode {
    std::vector<NodePtr> stmts;
    Block(std::vector<NodePtr> s,int l):ASTNode(l),stmts(std::move(s)){}
};

// ============================================================================
// 4단계: 파서 (재귀 하강) - C#의 Roslyn도 비슷한 방식입니다!
// ============================================================================
// 우선순위: or < and < 비교 < +- < */ < 단항 < 괄호/값
class Parser {
    std::vector<Token> toks_;
    size_t pos_;
    const Token& cur() const { return toks_[pos_]; }
    bool check(TokenType t) const { return cur().type==t; }
    bool match(TokenType t) { if (check(t)){pos_++;return true;} return false; }
    Token expect(TokenType t, const std::string& msg) {
        if (check(t)){auto tk=cur();pos_++;return tk;}
        throw std::runtime_error("[파싱오류] "+std::to_string(cur().line)+"줄: "+msg+" ('"+cur().value+"' 발견)");
    }
    void skipNL() { while (pos_<toks_.size()&&check(TokenType::NEWLINE)) pos_++; }

    // --- 수식 파싱 (우선순위별로 나뉨) ---
    NodePtr primary() {
        int l=cur().line;
        if (check(TokenType::NUMBER)) { double v=std::stod(cur().value); pos_++; return std::make_unique<NumberLit>(v,l); }
        if (check(TokenType::STRING)) { auto v=cur().value; pos_++; return std::make_unique<StringLit>(v,l); }
        if (check(TokenType::IDENTIFIER)) { auto n=cur().value; pos_++; return std::make_unique<VarAccess>(n,l); }
        if (match(TokenType::LPAREN)) { auto e=parseOr(); expect(TokenType::RPAREN,"')' 필요"); return e; }
        throw std::runtime_error("[파싱오류] "+std::to_string(l)+"줄: 수식 필요 ('"+cur().value+"' 발견)");
    }
    NodePtr unary() {
        int l=cur().line;
        if (match(TokenType::MINUS)) return std::make_unique<UnaryOp>("-",unary(),l);
        if (match(TokenType::NOT)) return std::make_unique<UnaryOp>("not",unary(),l);
        return primary();
    }
    NodePtr mul() {
        auto left=unary();
        while (check(TokenType::STAR)||check(TokenType::SLASH)) {
            auto op=cur().value; int l=cur().line; pos_++;
            left=std::make_unique<BinaryOp>(std::move(left),op,unary(),l);
        } return left;
    }
    NodePtr add() {
        auto left=mul();
        while (check(TokenType::PLUS)||check(TokenType::MINUS)) {
            auto op=cur().value; int l=cur().line; pos_++;
            left=std::make_unique<BinaryOp>(std::move(left),op,mul(),l);
        } return left;
    }
    NodePtr cmp() {
        auto left=add();
        while (check(TokenType::LESS)||check(TokenType::GREATER)||check(TokenType::LESS_EQUAL)||
               check(TokenType::GREATER_EQUAL)||check(TokenType::EQUAL_EQUAL)||check(TokenType::NOT_EQUAL)) {
            auto op=cur().value; int l=cur().line; pos_++;
            left=std::make_unique<BinaryOp>(std::move(left),op,add(),l);
        } return left;
    }
    NodePtr parseAnd() {
        auto left=cmp();
        while (match(TokenType::AND)) { int l=cur().line; left=std::make_unique<BinaryOp>(std::move(left),"and",cmp(),l); }
        return left;
    }
    NodePtr parseOr() {
        auto left=parseAnd();
        while (match(TokenType::OR)) { int l=cur().line; left=std::make_unique<BinaryOp>(std::move(left),"or",parseAnd(),l); }
        return left;
    }
    NodePtr parseExpr() { return parseOr(); }

    // --- 블록/문장 파싱 ---
    std::vector<NodePtr> parseBlock() {
        std::vector<NodePtr> s; skipNL();
        while (!check(TokenType::END)&&!check(TokenType::ELSE)&&!check(TokenType::END_OF_FILE))
            { s.push_back(parseStmt()); skipNL(); }
        return s;
    }
    NodePtr parseStmt() {
        skipNL(); int l=cur().line;
        // let 변수선언
        if (match(TokenType::LET)) {
            auto name=expect(TokenType::IDENTIFIER,"변수이름 필요");
            expect(TokenType::ASSIGN,"'=' 필요");
            return std::make_unique<VarDecl>(name.value,parseExpr(),l);
        }
        // print 출력문
        if (match(TokenType::PRINT)) return std::make_unique<PrintStmt>(parseExpr(),l);
        // if 조건문
        if (match(TokenType::IF)) {
            auto c=parseExpr(); skipNL(); auto tb=parseBlock();
            std::vector<NodePtr> eb;
            if (match(TokenType::ELSE)) { skipNL(); eb=parseBlock(); }
            expect(TokenType::END,"'end' 필요");
            return std::make_unique<IfStmt>(std::move(c),std::move(tb),std::move(eb),l);
        }
        // while 반복문
        if (match(TokenType::WHILE)) {
            auto c=parseExpr(); skipNL(); auto b=parseBlock();
            expect(TokenType::END,"'end' 필요");
            return std::make_unique<WhileStmt>(std::move(c),std::move(b),l);
        }
        // 변수 대입 (x = 값)
        if (check(TokenType::IDENTIFIER)) {
            auto name=cur().value; auto sp=pos_; pos_++;
            if (match(TokenType::ASSIGN)) return std::make_unique<VarAssign>(name,parseExpr(),l);
            pos_=sp;
        }
        return parseExpr();
    }

public:
    Parser(const std::vector<Token>& t) : toks_(t), pos_(0) {}
    std::vector<NodePtr> parse() {
        std::vector<NodePtr> prog; skipNL();
        while (!check(TokenType::END_OF_FILE)) { prog.push_back(parseStmt()); skipNL(); }
        return prog;
    }
};

// ============================================================================
// 5단계: 변수 환경 (스코프 체인)
// ============================================================================
// C#의 Dictionary<string, object>를 중첩해서 쓰는 것과 같습니다
//  전역스코프 { x=10 } ← if블록스코프 { z=30 } (안에서 바깥 변수를 찾을 수 있음!)
class Environment {
    std::unordered_map<std::string, Value> vars_;
    Environment* parent_;
public:
    Environment() : parent_(nullptr) {}
    Environment(Environment* p) : parent_(p) {}
    void define(const std::string& n, const Value& v) { vars_[n]=v; }
    Value get(const std::string& n, int l) const {
        auto it=vars_.find(n);
        if (it!=vars_.end()) return it->second;
        if (parent_) return parent_->get(n,l);
        throw std::runtime_error("[실행오류] "+std::to_string(l)+"줄: 정의안된 변수 '"+n+"'");
    }
    void set(const std::string& n, const Value& v, int l) {
        auto it=vars_.find(n);
        if (it!=vars_.end()) { it->second=v; return; }
        if (parent_) { parent_->set(n,v,l); return; }
        throw std::runtime_error("[실행오류] "+std::to_string(l)+"줄: 정의안된 변수 '"+n+"'");
    }
};

// ============================================================================
// 6단계: 인터프리터 - AST를 걸어다니며 실행 (Tree-Walking)
// ============================================================================
// C#의 Visitor 패턴과 비슷합니다!
class Interpreter {
    Environment global_;

    // 수식 계산 → 값 반환
    Value eval(ASTNode* n, Environment& env) {
        if (auto* x=dynamic_cast<NumberLit*>(n)) return x->value;
        if (auto* x=dynamic_cast<StringLit*>(n)) return x->value;
        if (auto* x=dynamic_cast<VarAccess*>(n)) return env.get(x->name, x->line);
        if (auto* x=dynamic_cast<UnaryOp*>(n)) {
            auto v=eval(x->operand.get(),env);
            if (x->op=="-") return -valNum(v);
            if (x->op=="not") return !truthy(v);
        }
        if (auto* x=dynamic_cast<BinaryOp*>(n)) {
            auto lv=eval(x->left.get(),env), rv=eval(x->right.get(),env);
            // 문자열 + → 연결 (C#에서도 "a"+"b" = "ab")
            if (x->op=="+"&&std::holds_alternative<std::string>(lv))
                return std::get<std::string>(lv)+valStr(rv);
            if (x->op=="+"&&std::holds_alternative<std::string>(rv))
                return valStr(lv)+std::get<std::string>(rv);
            double l=valNum(lv), r=valNum(rv);
            if (x->op=="+") return l+r;  if (x->op=="-") return l-r;
            if (x->op=="*") return l*r;
            if (x->op=="/") {
                if (r==0) throw std::runtime_error("[실행오류] "+std::to_string(x->line)+"줄: 0으로 나누기!");
                return l/r;
            }
            if (x->op=="<") return l<r;   if (x->op==">") return l>r;
            if (x->op=="<=") return l<=r;  if (x->op==">=") return l>=r;
            if (x->op=="==") return l==r;  if (x->op=="!=") return l!=r;
            if (x->op=="and") return truthy(lv)&&truthy(rv);
            if (x->op=="or") return truthy(lv)||truthy(rv);
        }
        throw std::runtime_error("[실행오류] "+std::to_string(n->line)+"줄: 알수없는 노드");
    }

    // 문장 실행
    void exec(ASTNode* n, Environment& env) {
        if (auto* x=dynamic_cast<VarDecl*>(n)) { env.define(x->name,eval(x->init.get(),env)); return; }
        if (auto* x=dynamic_cast<VarAssign*>(n)) { env.set(x->name,eval(x->value.get(),env),x->line); return; }
        if (auto* x=dynamic_cast<PrintStmt*>(n)) { std::cout<<valStr(eval(x->expr.get(),env))<<std::endl; return; }
        if (auto* x=dynamic_cast<IfStmt*>(n)) {
            auto& body = truthy(eval(x->cond.get(),env)) ? x->thenB : x->elseB;
            for (auto& s:body) exec(s.get(),env);
            return;
        }
        if (auto* x=dynamic_cast<WhileStmt*>(n)) {
            int cnt=0;
            while (truthy(eval(x->cond.get(),env))) {
                for (auto& s:x->body) exec(s.get(),env);
                if (++cnt>100000) throw std::runtime_error("[실행오류] "+std::to_string(x->line)+"줄: 무한루프?");
            }
            return;
        }
        if (auto* x=dynamic_cast<Block*>(n)) {
            Environment be(&env);
            for (auto& s:x->stmts) exec(s.get(),be);
            return;
        }
        eval(n,env); // 수식 문장
    }

public:
    void run(const std::string& src) {
        try {
            Lexer lex(src);
            auto toks=lex.tokenize();
            Parser par(toks);
            auto prog=par.parse();
            for (auto& s:prog) exec(s.get(),global_);
        } catch (const std::runtime_error& e) { std::cerr<<e.what()<<std::endl; }
    }

    // REPL용: 수식 결과를 출력합니다
    void runLine(const std::string& src) {
        try {
            Lexer lex(src); auto toks=lex.tokenize();
            Parser par(toks); auto prog=par.parse();
            for (auto& s:prog) {
                if (dynamic_cast<NumberLit*>(s.get())||dynamic_cast<StringLit*>(s.get())||
                    dynamic_cast<BinaryOp*>(s.get())||dynamic_cast<UnaryOp*>(s.get())||
                    dynamic_cast<VarAccess*>(s.get()))
                    std::cout<<"=> "<<valStr(eval(s.get(),global_))<<std::endl;
                else exec(s.get(),global_);
            }
        } catch (const std::runtime_error& e) { std::cerr<<e.what()<<std::endl; }
    }
};

// ============================================================================
// 7단계: 테스트 프로그램들
// ============================================================================

void testBasic(Interpreter& interp) {
    std::cout << "=== 예제 1: 기본 산술과 변수 ===" << std::endl;
    interp.run(R"(
let x = 10
let y = 20
print x + y
print x * y - 5
let name = "Hello, World!"
print name
)");
    std::cout << std::endl;
}

void testIf(Interpreter& interp) {
    std::cout << "=== 예제 2: 조건문 (if/else) ===" << std::endl;
    interp.run(R"(
let x = 10
if x > 5
  print "x is big"
end
let y = 3
if y > 5
  print "y is big"
else
  print "y is small"
end
)");
    std::cout << std::endl;
}

void testWhile(Interpreter& interp) {
    std::cout << "=== 예제 3: 1부터 10까지 합 ===" << std::endl;
    interp.run(R"(
let sum = 0
let i = 1
while i <= 10
  sum = sum + i
  i = i + 1
end
print sum
)");
    std::cout << std::endl;
}

void testMultTable(Interpreter& interp) {
    std::cout << "=== 예제 4: 구구단 5단 ===" << std::endl;
    interp.run(R"(
let n = 5
let i = 1
while i <= 9
  print n * i
  i = i + 1
end
)");
    std::cout << std::endl;
}

void testFibonacci(Interpreter& interp) {
    std::cout << "=== 예제 5: 피보나치 수열 (처음 10개) ===" << std::endl;
    interp.run(R"(
let a = 0
let b = 1
let count = 0
while count < 10
  print a
  let temp = b
  b = a + b
  a = temp
  count = count + 1
end
)");
    std::cout << std::endl;
}

void testStrings(Interpreter& interp) {
    std::cout << "=== 예제 6: 문자열 연결 ===" << std::endl;
    interp.run(R"(
let greeting = "안녕하세요, "
let target = "세계!"
print greeting + target
let score = 100
print "점수: " + score
)");
    std::cout << std::endl;
}

// ============================================================================
// 8단계: REPL (Read-Eval-Print Loop) - 대화형 모드
// ============================================================================
// Python이나 Node.js의 REPL과 같습니다. C#의 csi.exe와도 같습니다!
//  ┌──────────────────────────┐
//  │ mini> let x = 42         │
//  │ mini> print x + 8        │
//  │ 50                       │
//  │ mini> exit               │
//  └──────────────────────────┘
void runREPL() {
    std::cout << "==============================" << std::endl;
    std::cout << "  미니 언어 REPL" << std::endl;
    std::cout << "  exit=종료, help=도움말" << std::endl;
    std::cout << "==============================" << std::endl;

    Interpreter interp;
    std::string line;
    while (true) {
        std::cout << "mini> ";
        if (!std::getline(std::cin, line)) break;
        if (line.empty()) continue;
        if (line=="exit"||line=="quit") { std::cout<<"안녕히 가세요!"<<std::endl; break; }
        if (line=="help") {
            std::cout << "  let x = 값      변수선언\n  x = 값          대입\n"
                      << "  print 수식      출력\n  if/else/end     조건문\n"
                      << "  while/end       반복문\n  연산: + - * / > < >= <= == !=\n"
                      << "  논리: and or not\n" << std::endl;
            continue;
        }
        // 여러줄 입력 (if, while 블록)
        std::string full = line;
        int depth = 0;
        if (line.find("if ")==0||line.find("while ")==0) depth=1;
        while (depth > 0) {
            std::cout << "....  ";
            std::string more;
            if (!std::getline(std::cin, more)) break;
            full += "\n" + more;
            auto trimmed=more; auto fp=trimmed.find_first_not_of(" \t");
            if (fp!=std::string::npos) trimmed=trimmed.substr(fp);
            if (trimmed.find("if ")==0||trimmed.find("while ")==0) depth++;
            else if (trimmed=="end"||trimmed.find("end")==0) depth--;
        }
        interp.runLine(full);
    }
}

// ============================================================================
// 메인 함수
// ============================================================================
/*
=============================================================================
  실행 흐름 가이드
=============================================================================
  testBasic: let x = 10 / let y = 5 / print x+y → 출력 15
  testIf:    let x=10 / if x>5 → "big" / else "small"
  testWhile: while i<=5 → 1 2 3 4 5 출력
  testMultTable: 9x9 구구단
  testFibonacci: fib(10) → 0 1 1 2 3 5 8 13 21 34 55
  testStrings: "hello" + "world" 연결

  종합 예제:
    let x = 10, let y = 20
    print x+y → 30
    if x > 5 → "x is big"
    while i <= 10 → sum = 1+2+...+10 = 55
    print sum → 55

  REPL 모드 (--repl): 대화형으로 한 줄씩 평가
=============================================================================
*/

int main(int argc, char* argv[]) {
    std::cout << "============================================================" << std::endl;
    std::cout << "  미니 프로그래밍 언어 인터프리터" << std::endl;
    std::cout << "  구조: 소스코드 → [렉서] → 토큰 → [파서] → AST → [실행]" << std::endl;
    std::cout << "============================================================" << std::endl;
    std::cout << std::endl;

    if (argc > 1 && std::string(argv[1]) == "--repl") { runREPL(); return 0; }

    { Interpreter i; testBasic(i); }
    { Interpreter i; testIf(i); }
    { Interpreter i; testWhile(i); }
    { Interpreter i; testMultTable(i); }
    { Interpreter i; testFibonacci(i); }
    { Interpreter i; testStrings(i); }

    std::cout << "=== 종합 예제 ===" << std::endl;
    {
        Interpreter interp;
        interp.run(R"(
let x = 10
let y = 20
print x + y
if x > 5
  print "x is big"
end
let sum = 0
let i = 1
while i <= 10
  sum = sum + i
  i = i + 1
end
print sum
)");
        // → 출력:
        //   30
        //   x is big
        //   55
    }
    std::cout << std::endl;
    std::cout << "REPL 모드: ./main --repl" << std::endl;
    return 0;
}
