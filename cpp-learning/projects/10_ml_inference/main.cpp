// ============================================================================
// 10_ml_inference/main.cpp
// 머신러닝 추론 엔진 (ML Inference Engine)
// ============================================================================
// *** 왜 C++로 머신러닝을 할까요? ***
// TensorFlow, PyTorch, ONNX Runtime, TensorRT 전부 C++입니다!
// 이유: GPU 연동 (CUDA), SIMD 벡터화, 텐서의 메모리 배치 제어
//
// ┌─────────────────────────────────────────────┐
// │  입력 데이터                                │
// │    ▼                                        │
// │  [Matrix 연산] → W*x + b                   │
// │    ▼                                        │
// │  [활성화 함수] → ReLU, Sigmoid, Softmax     │
// │    ▼ (반복: 여러 층)                        │
// │  [Dense Layer] → [Dense Layer] → [출력]     │
// │                                             │
// │  [역전파 학습] ← 손실 함수 (Cross-Entropy)  │
// │  [모델 저장/불러오기] → 바이너리 파일        │
// └─────────────────────────────────────────────┘
// ============================================================================

#include <iostream>     // 화면 출력
#include <vector>       // 동적 배열. C#의 List<T>!
#include <cmath>        // 수학 함수 (exp, log, sqrt, tanh)
#include <random>       // 난수 (가중치 초기화)
#include <algorithm>    // min, max
#include <numeric>      // accumulate
#include <cassert>      // 디버그 검증
#include <string>       // 문자열
#include <fstream>      // 파일 읽기/쓰기 (모델 저장)
#include <iomanip>      // 출력 형식
#include <chrono>       // 시간 측정
#include <sstream>      // 문자열 스트림
#include <functional>   // 함수 객체

// ============================================================================
// 1. Matrix 클래스
// ============================================================================
// Matrix 클래스는 C#의 MathNet.Numerics의 Matrix<double>와 비슷합니다
// new/delete 대신 vector를 쓰는 것은 C#에서 GC 대신 ArrayPool을 쓰는 것과 비슷합니다
//
//  행렬 곱셈:  [a b] x [e f] = [ae+bg  af+bh]
//              [c d]   [g h]   [ce+dg  cf+dh]

class Matrix {
    int rows_, cols_;
    std::vector<double> data_;
public:
    Matrix() : rows_(0), cols_(0) {}
    Matrix(int r, int c) : rows_(r), cols_(c), data_(r*c, 0.0) {}
    Matrix(int r, int c, double fill) : rows_(r), cols_(c), data_(r*c, fill) {}

    int rows() const { return rows_; }
    int cols() const { return cols_; }
    int size() const { return rows_*cols_; }
    double& operator()(int r, int c) { return data_[r*cols_+c]; }
    const double& operator()(int r, int c) const { return data_[r*cols_+c]; }
    double* data() { return data_.data(); }
    const double* data() const { return data_.data(); }

    // 행렬 덧셈
    Matrix operator+(const Matrix& o) const {
        assert(rows_==o.rows_ && cols_==o.cols_);
        Matrix r(rows_,cols_);
        for (int i=0;i<size();i++) r.data_[i]=data_[i]+o.data_[i];
        return r;
    }
    // 행렬 뺄셈
    Matrix operator-(const Matrix& o) const {
        assert(rows_==o.rows_ && cols_==o.cols_);
        Matrix r(rows_,cols_);
        for (int i=0;i<size();i++) r.data_[i]=data_[i]-o.data_[i];
        return r;
    }
    // 스칼라 곱
    Matrix operator*(double s) const {
        Matrix r(rows_,cols_);
        for (int i=0;i<size();i++) r.data_[i]=data_[i]*s;
        return r;
    }
    // 행렬 곱셈 (핵심 연산!)
    Matrix matmul(const Matrix& o) const {
        assert(cols_==o.rows_);
        Matrix r(rows_, o.cols_);
        for (int i=0;i<rows_;i++)
            for (int k=0;k<cols_;k++) {
                double a_ik = data_[i*cols_+k];
                for (int j=0;j<o.cols_;j++)
                    r.data_[i*o.cols_+j] += a_ik * o.data_[k*o.cols_+j];
            }
        return r;
    }
    // 원소별 곱셈 (Hadamard product)
    Matrix element_multiply(const Matrix& o) const {
        assert(rows_==o.rows_ && cols_==o.cols_);
        Matrix r(rows_,cols_);
        for (int i=0;i<size();i++) r.data_[i]=data_[i]*o.data_[i];
        return r;
    }
    // 전치 (행과 열 교환)
    Matrix transpose() const {
        Matrix r(cols_,rows_);
        for (int i=0;i<rows_;i++)
            for (int j=0;j<cols_;j++) r(j,i)=(*this)(i,j);
        return r;
    }
    // 각 원소에 함수 적용 (C#의 LINQ Select와 비슷!)
    Matrix apply(std::function<double(double)> func) const {
        Matrix r(rows_,cols_);
        for (int i=0;i<size();i++) r.data_[i]=func(data_[i]);
        return r;
    }
    // 행 벡터를 모든 행에 더하기 (바이어스 브로드캐스트)
    Matrix add_row_vector(const Matrix& rv) const {
        assert(rv.rows_==1 && rv.cols_==cols_);
        Matrix r(rows_,cols_);
        for (int i=0;i<rows_;i++)
            for (int j=0;j<cols_;j++) r(i,j)=(*this)(i,j)+rv(0,j);
        return r;
    }
    // 열 방향 합계
    Matrix sum_columns() const {
        Matrix r(1,cols_,0.0);
        for (int i=0;i<rows_;i++)
            for (int j=0;j<cols_;j++) r(0,j)+=(*this)(i,j);
        return r;
    }
    double sum() const { double s=0; for (auto v:data_) s+=v; return s; }
    // 행별 최댓값 인덱스 (분류 결과)
    std::vector<int> argmax_per_row() const {
        std::vector<int> idx(rows_);
        for (int i=0;i<rows_;i++) {
            int best=0; double bv=(*this)(i,0);
            for (int j=1;j<cols_;j++) if ((*this)(i,j)>bv) { bv=(*this)(i,j); best=j; }
            idx[i]=best;
        }
        return idx;
    }
    // 랜덤 초기화 (He 초기화)
    static Matrix random(int r, int c, double scale, std::mt19937& rng) {
        Matrix m(r,c);
        std::normal_distribution<double> d(0.0, scale);
        for (int i=0;i<m.size();i++) m.data_[i]=d(rng);
        return m;
    }
    void print(const std::string& name="", int mr=5, int mc=5) const {
        if (!name.empty()) std::cout << "  " << name << " (" << rows_ << "x" << cols_ << "):\n";
        for (int i=0;i<std::min(rows_,mr);i++) {
            std::cout << "    [";
            for (int j=0;j<std::min(cols_,mc);j++) {
                std::cout << std::fixed << std::setprecision(4) << std::setw(8) << (*this)(i,j);
                if (j<std::min(cols_,mc)-1) std::cout << ",";
            }
            if (cols_>mc) std::cout << ",...";
            std::cout << "]\n";
        }
        if (rows_>mr) std::cout << "    ...(" << rows_-mr << " more)\n";
    }
    // 바이너리 저장/불러오기
    bool save(std::ofstream& f) const {
        f.write((const char*)&rows_, sizeof(int));
        f.write((const char*)&cols_, sizeof(int));
        f.write((const char*)data_.data(), data_.size()*sizeof(double));
        return f.good();
    }
    bool load(std::ifstream& f) {
        f.read((char*)&rows_, sizeof(int));
        f.read((char*)&cols_, sizeof(int));
        data_.resize(rows_*cols_);
        f.read((char*)data_.data(), data_.size()*sizeof(double));
        return f.good();
    }
};

// ============================================================================
// 2. 활성화 함수
// ============================================================================
// 신경망에 비선형성을 부여합니다
//  ReLU:    f(x) = max(0, x)   ← 가장 인기!
//  Sigmoid: f(x) = 1/(1+e^-x)  ← 확률 출력
//  Tanh:    f(x) = tanh(x)      ← -1~1 범위
//  Softmax: 확률 분포로 변환     ← 분류의 마지막 층

namespace Activations {
    Matrix relu(const Matrix& x) { return x.apply([](double v){ return std::max(0.0,v); }); }
    Matrix relu_derivative(const Matrix& x) { return x.apply([](double v){ return v>0?1.0:0.0; }); }

    Matrix sigmoid(const Matrix& x) {
        return x.apply([](double v) {
            if (v>500) return 1.0; if (v<-500) return 0.0;
            return 1.0/(1.0+std::exp(-v));
        });
    }
    Matrix sigmoid_derivative(const Matrix& out) {
        return out.element_multiply(out.apply([](double v){ return 1.0-v; }));
    }

    Matrix tanh_act(const Matrix& x) { return x.apply([](double v){ return std::tanh(v); }); }
    Matrix tanh_derivative(const Matrix& out) { return out.apply([](double v){ return 1.0-v*v; }); }

    // Softmax: 출력을 확률 분포로 (합=1)
    Matrix softmax(const Matrix& x) {
        Matrix r(x.rows(), x.cols());
        for (int i=0;i<x.rows();i++) {
            double mx = x(i,0);
            for (int j=1;j<x.cols();j++) mx=std::max(mx,x(i,j));
            double sum=0;
            for (int j=0;j<x.cols();j++) { r(i,j)=std::exp(x(i,j)-mx); sum+=r(i,j); }
            for (int j=0;j<x.cols();j++) r(i,j)/=sum;
        }
        return r;
    }
}

// ============================================================================
// 3. Dense Layer (완전 연결 층)
// ============================================================================
// 신경망의 Layer는 C#에서 interface ILayer { Matrix Forward(Matrix input); }와 같습니다
//  output = activation(input * weights + bias)
//
//  입력(3) → 출력(2):
//    x1 ──┬──w11──▶ y1 = activation(w11*x1 + w21*x2 + w31*x3 + b1)
//    x2 ──┤
//    x3 ──┘

enum class ActivationType { None, ReLU, Sigmoid, Tanh, Softmax };

class DenseLayer {
public:
    Matrix weights, bias;
    ActivationType activation;
    Matrix last_input, last_z, last_output;  // 순전파 중간값 (역전파용)
    Matrix grad_weights, grad_bias;

    DenseLayer() : activation(ActivationType::None) {}
    DenseLayer(int in, int out, ActivationType act, std::mt19937& rng) : activation(act) {
        double scale = std::sqrt(2.0/in);  // He 초기화
        weights = Matrix::random(in, out, scale, rng);
        bias = Matrix(1, out, 0.0);
    }

    // 순전파 (Forward Pass)
    Matrix forward(const Matrix& input) {
        last_input = input;
        last_z = input.matmul(weights).add_row_vector(bias);
        switch (activation) {
            case ActivationType::ReLU:    last_output = Activations::relu(last_z); break;
            case ActivationType::Sigmoid: last_output = Activations::sigmoid(last_z); break;
            case ActivationType::Tanh:    last_output = Activations::tanh_act(last_z); break;
            case ActivationType::Softmax: last_output = Activations::softmax(last_z); break;
            default: last_output = last_z;
        }
        return last_output;
    }

    // 역전파 (Backward Pass)
    Matrix backward(const Matrix& grad_out) {
        Matrix grad_z;
        switch (activation) {
            case ActivationType::ReLU:    grad_z = grad_out.element_multiply(Activations::relu_derivative(last_z)); break;
            case ActivationType::Sigmoid: grad_z = grad_out.element_multiply(Activations::sigmoid_derivative(last_output)); break;
            case ActivationType::Tanh:    grad_z = grad_out.element_multiply(Activations::tanh_derivative(last_output)); break;
            case ActivationType::Softmax: grad_z = grad_out; break;  // Softmax+CE 합쳐진 기울기
            default: grad_z = grad_out;
        }
        int bs = last_input.rows();
        grad_weights = last_input.transpose().matmul(grad_z) * (1.0/bs);
        grad_bias = grad_z.sum_columns() * (1.0/bs);
        return grad_z.matmul(weights.transpose());  // 이전 층으로 전달
    }

    void update_weights(double lr) {
        weights = weights - grad_weights * lr;
        bias = bias - grad_bias * lr;
    }
};

// ============================================================================
// 4. 신경망 (Neural Network)
// ============================================================================
// 여러 Dense Layer를 쌓아서 신경망을 만듭니다!
//  입력층 → 은닉층 → 은닉층 → 출력층

class NeuralNetwork {
    std::vector<DenseLayer> layers_;
    std::mt19937 rng_;
public:
    explicit NeuralNetwork(unsigned seed = 42) : rng_(seed) {}

    void add_layer(int in, int out, ActivationType act) {
        layers_.emplace_back(in, out, act, rng_);
    }

    Matrix forward(const Matrix& input) {
        Matrix cur = input;
        for (auto& l : layers_) cur = l.forward(cur);
        return cur;
    }

    double cross_entropy_loss(const Matrix& pred, const Matrix& target) {
        double loss = 0;
        for (int i=0;i<pred.rows();i++)
            for (int j=0;j<pred.cols();j++)
                loss -= target(i,j) * std::log(std::max(pred(i,j), 1e-15));
        return loss / pred.rows();
    }

    double mse_loss(const Matrix& pred, const Matrix& target) {
        double loss = 0;
        for (int i=0;i<pred.rows();i++)
            for (int j=0;j<pred.cols();j++) {
                double d = pred(i,j)-target(i,j); loss += d*d;
            }
        return loss / (pred.rows()*pred.cols());
    }

    // 학습 한 스텝: 순전파 → 역전파 → 가중치 갱신
    void train_step(const Matrix& input, const Matrix& target, double lr) {
        Matrix output = forward(input);
        Matrix grad = output - target;  // 손실의 기울기
        for (int i=(int)layers_.size()-1;i>=0;i--) grad = layers_[i].backward(grad);
        for (auto& l : layers_) l.update_weights(lr);
    }

    double accuracy(const Matrix& pred, const Matrix& target) {
        auto pc = pred.argmax_per_row(), tc = target.argmax_per_row();
        int correct = 0;
        for (size_t i=0;i<pc.size();i++) if (pc[i]==tc[i]) correct++;
        return (double)correct/pc.size();
    }

    bool save_model(const std::string& path) {
        std::ofstream f(path, std::ios::binary);
        if (!f.is_open()) return false;
        int n=(int)layers_.size();
        f.write((const char*)&n, sizeof(int));
        for (auto& l : layers_) {
            int act=(int)l.activation;
            f.write((const char*)&act, sizeof(int));
            l.weights.save(f); l.bias.save(f);
        }
        return f.good();
    }

    bool load_model(const std::string& path) {
        std::ifstream f(path, std::ios::binary);
        if (!f.is_open()) return false;
        int n; f.read((char*)&n, sizeof(int));
        layers_.resize(n);
        for (auto& l : layers_) {
            int act; f.read((char*)&act, sizeof(int));
            l.activation = (ActivationType)act;
            l.weights.load(f); l.bias.load(f);
        }
        return f.good();
    }
    int layer_count() const { return (int)layers_.size(); }
};

// ============================================================================
// 5. 데이터 생성
// ============================================================================

namespace DataUtils {
    // XOR 데이터: (0,0)→0, (0,1)→1, (1,0)→1, (1,1)→0
    std::pair<Matrix,Matrix> generate_xor() {
        Matrix in(4,2), out(4,1);
        in(0,0)=0;in(0,1)=0; out(0,0)=0;
        in(1,0)=0;in(1,1)=1; out(1,0)=1;
        in(2,0)=1;in(2,1)=0; out(2,0)=1;
        in(3,0)=1;in(3,1)=1; out(3,0)=0;
        return {in, out};
    }

    // 원형 분류: 안쪽=클래스0, 바깥쪽=클래스1
    std::pair<Matrix,Matrix> generate_circles(int n, double noise, std::mt19937& rng) {
        Matrix in(n,2), out(n,2);
        std::normal_distribution<double> nd(0,noise);
        std::uniform_real_distribution<double> ad(0,6.2832), rd(0,1.0);
        for (int i=0;i<n;i++) {
            double ang=ad(rng), r;
            int label;
            if (i<n/2) { r=rd(rng)*0.5; label=0; } else { r=0.5+rd(rng)*0.5; label=1; }
            in(i,0)=r*std::cos(ang)+nd(rng);
            in(i,1)=r*std::sin(ang)+nd(rng);
            out(i,label)=1.0;
        }
        return {in, out};
    }

    // MNIST 스타일 합성 숫자 (4x4=16 픽셀, 3 클래스)
    std::pair<Matrix,Matrix> generate_digits(int n_per_class, std::mt19937& rng) {
        // 숫자 0, 1, 2의 4x4 패턴
        std::vector<std::vector<double>> patterns = {
            {1,1,0,0, 1,0,0,1, 1,0,0,1, 0,1,1,0},  // 0
            {0,1,0,0, 1,1,0,0, 0,1,0,0, 1,1,1,0},  // 1
            {1,1,1,0, 0,0,1,0, 0,1,0,0, 1,1,1,0},  // 2
        };
        int nc=(int)patterns.size(), total=n_per_class*nc;
        Matrix in(total,16), out(total,nc);
        std::normal_distribution<double> nd(0,0.1);
        int idx=0;
        for (int c=0;c<nc;c++)
            for (int s=0;s<n_per_class;s++) {
                for (int f=0;f<16;f++) in(idx,f)=patterns[c][f]+nd(rng);
                out(idx,c)=1.0;
                idx++;
            }
        return {in, out};
    }
}

// ============================================================================
// main
// ============================================================================
/*
=============================================================================
  실행 흐름 가이드 (시드 42 고정)
=============================================================================
  [1] Matrix:
      A(2x3) = [[1,2,3], [4,5,6]]
      B(3x2) = [[7,8], [9,10], [11,12]]
      A*B = [[58,64], [139,154]]   (예: 1*7+2*9+3*11=58)
      A^T = [[1,4], [2,5], [3,6]]
      A.*D (element-wise) = [[2,4,6], [12,15,18]]

  [2] Activation:
      입력 = [-2,-1,0,1,2]
      ReLU = [0,0,0,1,2]
      Sigmoid = [0.119,0.269,0.5,0.731,0.881]
      Tanh = [-0.964,-0.762,0,0.762,0.964]
      Softmax([2,1,0.1]) = [0.659,0.242,0.099], 합=1.0

  [3] XOR 학습:
      구조: 2 → 8(ReLU) → 1(Sigmoid)
      데이터: (0,0)→0, (0,1)→1, (1,0)→1, (1,1)→0
      epoch 0: Loss ~0.25
      epoch 400: Loss ~0.005
      epoch 2000: Loss ~0.0001
      최종: 거의 정답에 수렴

  [4] Circle classification:
      200 샘플, 2층 숨김
      epoch 500까지 정확도 95%+ 도달

  [5] 합성 숫자 분류:
      train 50, test 20
      train 정확도 ~100%, test ~85~95%

  [6] 모델 저장/불러오기:
      원본 출력 ≈ 불러온 출력 (차이 0)
      "차이: 0.00e+00"

  [7] 추론 벤치마크:
      64-128-64-10 모델, batch=100, 1000 iter
      총: ~수백ms, 샘플당: ~수us
      처리량: ~수십~수백K samples/sec

  [8] 행렬 곱셈 GFLOPS:
      32x32: ~0.X GFLOPS (단순 구현, BLAS 사용 시 100배 가능)
      64x64: ~1 GFLOPS
      128x128: ~1.5 GFLOPS
      256x256: ~2 GFLOPS
=============================================================================
*/

int main() {
    std::cout << "============================================================\n";
    std::cout << "  머신러닝 추론 엔진 (ML Inference Engine)\n";
    std::cout << "============================================================\n\n";

    std::mt19937 rng(42);

    std::cout << "--- 1. Matrix 기본 연산 ---\n";
    {
        Matrix a(2,3);
        a(0,0)=1;a(0,1)=2;a(0,2)=3; a(1,0)=4;a(1,1)=5;a(1,2)=6;
        // → A = [[1,2,3], [4,5,6]]
        Matrix b(3,2);
        b(0,0)=7;b(0,1)=8; b(1,0)=9;b(1,1)=10; b(2,0)=11;b(2,1)=12;
        // → B = [[7,8], [9,10], [11,12]]
        a.print("A"); b.print("B");
        a.matmul(b).print("A*B");
        // → A*B[0,0] = 1*7+2*9+3*11 = 58
        //   A*B[0,1] = 1*8+2*10+3*12 = 64
        //   A*B[1,0] = 4*7+5*9+6*11 = 139
        //   A*B[1,1] = 4*8+5*10+6*12 = 154
        a.transpose().print("A^T");
        // → A^T = [[1,4], [2,5], [3,6]]
        Matrix d(2,3);
        d(0,0)=2;d(0,1)=2;d(0,2)=2; d(1,0)=3;d(1,1)=3;d(1,2)=3;
        a.element_multiply(d).print("A.*D");
        // → element-wise: [[1*2,2*2,3*2], [4*3,5*3,6*3]]
        //               = [[2,4,6], [12,15,18]]
    }

    // --- 2. 활성화 함수 ---
    std::cout << "\n--- 2. 활성화 함수 ---\n";
    {
        Matrix x(1,5);
        x(0,0)=-2;x(0,1)=-1;x(0,2)=0;x(0,3)=1;x(0,4)=2;
        x.print("입력"); Activations::relu(x).print("ReLU");
        Activations::sigmoid(x).print("Sigmoid"); Activations::tanh_act(x).print("Tanh");
        Matrix logits(1,3); logits(0,0)=2;logits(0,1)=1;logits(0,2)=0.1;
        Activations::softmax(logits).print("Softmax");
        std::cout << "  Softmax 합: " << Activations::softmax(logits).sum() << " (=1.0!)\n";
    }

    // --- 3. XOR 학습 (역전파) ---
    std::cout << "\n--- 3. XOR 학습 ---\n";
    {
        auto [inputs, targets] = DataUtils::generate_xor();
        NeuralNetwork nn(42);
        nn.add_layer(2, 8, ActivationType::ReLU);
        nn.add_layer(8, 1, ActivationType::Sigmoid);
        std::cout << "  구조: 2 -> 8(ReLU) -> 1(Sigmoid), lr=0.5\n\n";

        for (int ep=0;ep<=2000;ep++) {
            nn.train_step(inputs, targets, 0.5);
            if (ep%400==0) {
                Matrix p = nn.forward(inputs);
                std::cout << std::fixed << std::setprecision(4);
                std::cout << "  Epoch " << std::setw(5) << ep << " | Loss: "
                          << nn.mse_loss(p,targets) << " | [";
                for (int i=0;i<4;i++) { std::cout << p(i,0); if (i<3) std::cout << ","; }
                std::cout << "]\n";
            }
        }
        std::cout << "\n  최종 XOR:\n";
        Matrix fp = nn.forward(inputs);
        for (int i=0;i<4;i++)
            std::cout << "    (" << inputs(i,0) << "," << inputs(i,1) << ") -> "
                      << std::setprecision(4) << fp(i,0) << " (정답:" << targets(i,0) << ")\n";
    }

    // --- 4. 원형 분류 (Softmax + Cross-Entropy) ---
    std::cout << "\n--- 4. 원형 분류 ---\n";
    {
        auto [in, tgt] = DataUtils::generate_circles(200, 0.05, rng);
        NeuralNetwork nn(123);
        nn.add_layer(2, 16, ActivationType::ReLU);
        nn.add_layer(16, 8, ActivationType::ReLU);
        nn.add_layer(8, 2, ActivationType::Softmax);
        std::cout << "  200개, 2->16(ReLU)->8(ReLU)->2(Softmax)\n\n";

        for (int ep=0;ep<=500;ep++) {
            nn.train_step(in, tgt, 0.1);
            if (ep%100==0) {
                Matrix p = nn.forward(in);
                std::cout << std::fixed << std::setprecision(4);
                std::cout << "  Epoch " << std::setw(4) << ep
                          << " | Loss: " << nn.cross_entropy_loss(p,tgt)
                          << " | Acc: " << nn.accuracy(p,tgt)*100 << "%\n";
            }
        }
    }

    // --- 5. MNIST 스타일 숫자 분류 ---
    std::cout << "\n--- 5. 숫자 분류 (합성 데이터) ---\n";
    {
        auto [train_d, train_l] = DataUtils::generate_digits(50, rng);
        NeuralNetwork nn(77);
        nn.add_layer(16, 32, ActivationType::ReLU);
        nn.add_layer(32, 16, ActivationType::ReLU);
        nn.add_layer(16, 3, ActivationType::Softmax);
        std::cout << "  " << train_d.rows() << "개, 16->32->16->3\n\n";

        for (int ep=0;ep<=300;ep++) {
            nn.train_step(train_d, train_l, 0.05);
            if (ep%50==0) {
                Matrix p = nn.forward(train_d);
                std::cout << std::fixed << std::setprecision(4);
                std::cout << "  Epoch " << std::setw(4) << ep
                          << " | Loss: " << nn.cross_entropy_loss(p,train_l)
                          << " | Acc: " << nn.accuracy(p,train_l)*100 << "%\n";
            }
        }
        auto [test_d, test_l] = DataUtils::generate_digits(20, rng);
        Matrix tp = nn.forward(test_d);
        std::cout << "  테스트 정확도: " << nn.accuracy(tp,test_l)*100 << "%\n";
    }

    // --- 6. 모델 저장/불러오기 ---
    std::cout << "\n--- 6. 모델 저장/불러오기 ---\n";
    {
        NeuralNetwork orig(42);
        orig.add_layer(2, 8, ActivationType::ReLU);
        orig.add_layer(8, 1, ActivationType::Sigmoid);
        auto [in, tgt] = DataUtils::generate_xor();
        for (int i=0;i<2000;i++) orig.train_step(in, tgt, 0.5);

        Matrix op = orig.forward(in);
        std::cout << "  원본: [";
        for (int i=0;i<4;i++) { std::cout << std::fixed << std::setprecision(3) << op(i,0); if(i<3) std::cout << ","; }
        std::cout << "]\n";

        std::string path = "xor_model.bin";
        std::cout << "  저장: " << (orig.save_model(path)?"OK":"FAIL") << "\n";

        NeuralNetwork loaded;
        std::cout << "  불러오기: " << (loaded.load_model(path)?"OK":"FAIL") << "\n";

        Matrix lp = loaded.forward(in);
        std::cout << "  불러온: [";
        for (int i=0;i<4;i++) { std::cout << std::fixed << std::setprecision(3) << lp(i,0); if(i<3) std::cout << ","; }
        std::cout << "]\n";

        double diff = 0;
        for (int i=0;i<4;i++) diff += std::abs(op(i,0)-lp(i,0));
        std::cout << "  차이: " << std::scientific << diff << " (0이어야 함!)\n";
        std::remove(path.c_str());
    }

    // --- 7. 추론 벤치마크 ---
    std::cout << "\n--- 7. 추론 벤치마크 ---\n";
    {
        NeuralNetwork nn(99);
        nn.add_layer(64, 128, ActivationType::ReLU);
        nn.add_layer(128, 64, ActivationType::ReLU);
        nn.add_layer(64, 10, ActivationType::Softmax);

        int batch=100, iters=1000;
        Matrix input = Matrix::random(batch, 64, 1.0, rng);

        auto start = std::chrono::high_resolution_clock::now();
        Matrix last_out;
        for (int i=0;i<iters;i++) last_out = nn.forward(input);
        auto end = std::chrono::high_resolution_clock::now();

        auto us = std::chrono::duration_cast<std::chrono::microseconds>(end-start).count();
        double ms = us/1000.0;
        double per_sample = (double)us/iters/batch;

        std::cout << "  64->128->64->10, batch=" << batch << ", iters=" << iters << "\n";
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "  총: " << ms << "ms, 샘플당: " << per_sample << "us\n";
        std::cout << "  처리량: " << 1000000.0/per_sample << " samples/sec\n";
    }

    // --- 8. 행렬 곱셈 벤치마크 ---
    std::cout << "\n--- 8. 행렬 곱셈 벤치마크 ---\n";
    {
        for (int sz : {32, 64, 128, 256}) {
            Matrix a = Matrix::random(sz,sz,1.0,rng);
            Matrix b = Matrix::random(sz,sz,1.0,rng);
            int it = (sz<=64)?100:(sz<=128?20:5);
            auto start = std::chrono::high_resolution_clock::now();
            for (int i=0;i<it;i++) { Matrix c = a.matmul(b); }
            auto end = std::chrono::high_resolution_clock::now();
            double ms = std::chrono::duration_cast<std::chrono::microseconds>(end-start).count()/1000.0/it;
            double gflops = (2.0*sz*sz*sz)/(ms*1e6);
            std::cout << std::fixed << std::setprecision(3);
            std::cout << "  " << sz << "x" << sz << ": " << ms << "ms (" << gflops << " GFLOPS)\n";
        }
    }

    std::cout << "\n============================================================\n";
    std::cout << "  Python: 편리한 학습 / C#(ML.NET): 닷넷 ML\n";
    std::cout << "  C++: 실시간 추론, GPU(CUDA), SIMD, 메모리 제어\n";
    std::cout << "  마이크로초 추론, 임베디드/모바일 실행 가능!\n";
    std::cout << "============================================================\n";
    return 0;
}
