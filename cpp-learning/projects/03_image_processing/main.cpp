/**
 * ============================================================================
 *  프로젝트 03: 이미지 처리 엔진 (Image Processing Engine)
 * ============================================================================
 *
 *  왜 C++로 이미지 처리를 할까요?
 *  ─────────────────────────────
 *  1. 직접 메모리 접근: 픽셀 데이터를 포인터로 바로 조작합니다.
 *     C#에서는 Bitmap.LockBits()로 unsafe 모드에 들어가야 하지만,
 *     C++에서는 기본적으로 메모리를 직접 다룹니다.
 *
 *  2. Boxing/Unboxing 없음: C#에서 byte를 object로 변환할 때 발생하는
 *     boxing이 C++에는 없습니다. 100만 픽셀을 처리할 때 큰 차이입니다.
 *
 *  3. SIMD 잠재력: SSE/AVX 명령어로 한 번에 여러 픽셀을 처리할 수 있습니다.
 *     OpenCV가 C++인 이유가 바로 이것입니다.
 *
 *  4. 캐시 친화적: 픽셀을 연속 메모리(byte 배열)에 저장하므로
 *     CPU 캐시 히트율이 높아 매우 빠릅니다.
 *
 *  컴파일 방법: g++ -std=c++17 -O2 -o image_engine main.cpp
 * ============================================================================
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>    // uint8_t, uint32_t 등 — C#의 byte, uint와 같습니다
#include <cmath>      // sin, cos, sqrt 등 수학 함수
#include <algorithm>  // std::clamp, std::min, std::max — C#의 Math.Clamp()와 같습니다
#include <string>
#include <chrono>     // 시간 측정 — C#의 Stopwatch와 같습니다
#include <array>
#include <numeric>    // std::accumulate — C#의 LINQ .Sum()과 같습니다
#include <iomanip>    // std::setw, std::setprecision — 출력 포맷팅

// ============================================================================
//  BMP 파일 구조 (ASCII 아트)
// ============================================================================
//
//  BMP 파일은 이렇게 생겼습니다 (마치 택배 상자와 같아요!):
//
//  ┌─────────────────────────────────────────────────┐
//  │  BMP File Header (14 bytes) — 택배 송장         │
//  │  ┌─────────────────────────────────────────────┐ │
//  │  │ 'B','M'  (2 bytes) — "나는 BMP야!" 표시    │ │
//  │  │ fileSize (4 bytes) — 파일 전체 크기         │ │
//  │  │ reserved (4 bytes) — 예약된 공간            │ │
//  │  │ dataOffset(4 bytes) — 픽셀 데이터 시작 위치 │ │
//  │  └─────────────────────────────────────────────┘ │
//  │  DIB Header (40 bytes) — 상품 설명서            │
//  │  ┌─────────────────────────────────────────────┐ │
//  │  │ headerSize (4 bytes) — 이 설명서의 크기     │ │
//  │  │ width      (4 bytes) — 가로 픽셀 수         │ │
//  │  │ height     (4 bytes) — 세로 픽셀 수         │ │
//  │  │ planes     (2 bytes) — 항상 1               │ │
//  │  │ bpp        (2 bytes) — 픽셀당 비트(24=RGB)  │ │
//  │  │ compression(4 bytes) — 압축 방식(0=없음)    │ │
//  │  │ imageSize  (4 bytes) — 픽셀 데이터 크기     │ │
//  │  │ ... 기타 정보들 ...                         │ │
//  │  └─────────────────────────────────────────────┘ │
//  │  Pixel Data — 실제 그림 데이터 (택배 내용물)    │
//  │  ┌─────────────────────────────────────────────┐ │
//  │  │ B G R | B G R | B G R | padding...          │ │
//  │  │ B G R | B G R | B G R | padding...          │ │
//  │  │ (아래 줄부터 위로 저장! 뒤집어져 있어요!)   │ │
//  │  └─────────────────────────────────────────────┘ │
//  └─────────────────────────────────────────────────┘
//
//  주의: BMP는 BGR 순서! (RGB가 아닙니다)
//  주의: 각 행(row)은 4바이트 배수로 패딩됩니다!
//

// ============================================================================
//  픽셀 레이아웃 (ASCII 아트)
// ============================================================================
//
//  메모리에서 이미지를 1차원 배열로 저장합니다:
//  (C#의 Bitmap.LockBits()로 얻는 byte[]와 같은 원리입니다)
//
//  픽셀 (x, y) 위치:
//
//    y=0: [R G B] [R G B] [R G B] [R G B]  ← 첫 번째 줄
//    y=1: [R G B] [R G B] [R G B] [R G B]  ← 두 번째 줄
//    y=2: [R G B] [R G B] [R G B] [R G B]  ← 세 번째 줄
//
//    인덱스 계산: index = (y * width + x) * 3
//    이것은 C#에서 stride * y + x * 3 과 같은 공식입니다.
//
//    메모리 연속 저장 (캐시 친화적!):
//    [R₀₀ G₀₀ B₀₀ R₁₀ G₁₀ B₁₀ R₂₀ G₂₀ B₂₀ ... ]
//     ↑ (0,0)      ↑ (1,0)      ↑ (2,0)
//

// ============================================================================
//  구조체 정의
// ============================================================================

// BMP 파일 헤더 — C#의 [StructLayout(LayoutKind.Sequential)]와 같습니다
// pragma pack(push, 1)은 패딩 없이 메모리를 꽉 채우라는 뜻입니다
// C#에서 Pack = 1 옵션과 같습니다
#pragma pack(push, 1)
struct BMPFileHeader {
    uint16_t type{0x4D42};     // 'BM' — BMP 파일 시그니처 (매직 넘버)
    uint32_t size{0};          // 파일 전체 크기 (bytes)
    uint16_t reserved1{0};     // 예약됨 (사용 안 함)
    uint16_t reserved2{0};     // 예약됨 (사용 안 함)
    uint32_t offset{54};       // 픽셀 데이터 시작 위치 (14 + 40 = 54)
};

struct BMPInfoHeader {
    uint32_t size{40};         // 이 헤더의 크기 (항상 40)
    int32_t  width{0};         // 이미지 가로 크기
    int32_t  height{0};        // 이미지 세로 크기 (양수 = 아래→위)
    uint16_t planes{1};        // 색상 평면 수 (항상 1)
    uint16_t bitCount{24};     // 픽셀당 비트 수 (24 = RGB)
    uint32_t compression{0};   // 압축 방식 (0 = 비압축)
    uint32_t imageSize{0};     // 픽셀 데이터 크기
    int32_t  xPPM{2835};       // 가로 해상도 (pixels per meter)
    int32_t  yPPM{2835};       // 세로 해상도
    uint32_t colorsUsed{0};    // 사용된 색상 수 (0 = 전부)
    uint32_t colorsImportant{0}; // 중요한 색상 수
};
#pragma pack(pop)

// RGB 픽셀 — 하나의 점(dot)을 나타냅니다
// C#의 Color 구조체와 비슷하지만, 훨씬 가볍습니다 (3바이트만!)
struct Pixel {
    uint8_t r{0};  // 빨강 (0~255)
    uint8_t g{0};  // 초록 (0~255)
    uint8_t b{0};  // 파랑 (0~255)
};

// HSV 색상 — 색상(Hue), 채도(Saturation), 명도(Value)
// 포토샵의 HSB 색상 선택기와 같은 원리입니다
struct HSV {
    float h{0.0f};  // 색상: 0~360도 (빨강→주황→노랑→초록→파랑→보라→빨강)
    float s{0.0f};  // 채도: 0.0~1.0 (0=회색, 1=선명한 색)
    float v{0.0f};  // 명도: 0.0~1.0 (0=검정, 1=밝음)
};

// ============================================================================
//  Image 클래스 — 이미지를 메모리에 저장하고 조작하는 핵심 클래스
// ============================================================================
// C#의 Bitmap 클래스와 비슷한 역할이지만,
// 내부 구현을 직접 볼 수 있고 제어할 수 있습니다.

class Image {
private:
    int width_;
    int height_;
    // byte 배열은 C#의 byte[]와 같습니다
    // 이미지를 1차원 배열로 저장하는 이유: C#의 Bitmap.LockBits()와 같은 원리입니다
    // 연속 메모리에 저장해야 CPU 캐시가 효율적으로 동작합니다
    std::vector<uint8_t> data_;  // R, G, B, R, G, B, ... 순서로 저장

public:
    // 생성자 — 빈 이미지를 만듭니다 (검은색으로 초기화)
    // C#의 new Bitmap(width, height)와 같습니다
    Image(int w, int h) : width_(w), height_(h), data_(w * h * 3, 0) {}

    // 기본 접근자 — C#의 프로퍼티(Property)와 같습니다
    int width() const { return width_; }
    int height() const { return height_; }
    int totalPixels() const { return width_ * height_; }

    // 원본 데이터 포인터 — C#의 unsafe에서 byte* 포인터를 얻는 것과 같습니다
    uint8_t* rawData() { return data_.data(); }
    const uint8_t* rawData() const { return data_.data(); }

    // ────────────────────────────────────────────
    //  픽셀 접근 — 특정 좌표의 색상을 읽고 쓰기
    // ────────────────────────────────────────────

    // 픽셀 읽기 — C#의 Bitmap.GetPixel(x, y)과 같습니다
    Pixel getPixel(int x, int y) const {
        // 범위 검사 — 배열 밖을 읽으면 큰일나니까요!
        if (x < 0 || x >= width_ || y < 0 || y >= height_) {
            return {0, 0, 0};  // 범위 밖은 검은색 반환
        }
        int idx = (y * width_ + x) * 3;  // 1차원 인덱스 계산
        return {data_[idx], data_[idx + 1], data_[idx + 2]};
    }

    // 픽셀 쓰기 — C#의 Bitmap.SetPixel(x, y, color)과 같습니다
    void setPixel(int x, int y, const Pixel& p) {
        if (x < 0 || x >= width_ || y < 0 || y >= height_) return;
        int idx = (y * width_ + x) * 3;
        data_[idx] = p.r;
        data_[idx + 1] = p.g;
        data_[idx + 2] = p.b;
    }

    // ────────────────────────────────────────────
    //  BMP 파일 읽기/쓰기
    // ────────────────────────────────────────────

    // BMP 파일 저장 — C#의 Bitmap.Save("file.bmp")과 같습니다
    bool saveBMP(const std::string& filename) const {
        // 파일을 바이너리로 여는 것은 C#의 new BinaryWriter(File.Open(...))과 같습니다
        std::ofstream file(filename, std::ios::binary);
        if (!file) {
            std::cerr << "  [오류] 파일을 열 수 없습니다: " << filename << "\n";
            return false;
        }

        // BMP 행(row) 패딩 계산 — 각 행은 4바이트 배수여야 합니다
        // 예: 너비 3픽셀 × 3바이트 = 9바이트 → 12바이트로 패딩 (3바이트 추가)
        int rowSize = width_ * 3;
        int padding = (4 - (rowSize % 4)) % 4;
        int paddedRowSize = rowSize + padding;

        // 헤더 작성
        BMPFileHeader fileHeader;
        fileHeader.size = 54 + paddedRowSize * height_;

        BMPInfoHeader infoHeader;
        infoHeader.width = width_;
        infoHeader.height = height_;
        infoHeader.imageSize = paddedRowSize * height_;

        // reinterpret_cast는 C#의 unsafe 코드에서 포인터 캐스팅과 비슷합니다
        // 구조체의 메모리를 그대로 바이트로 써버리는 것입니다
        file.write(reinterpret_cast<const char*>(&fileHeader), sizeof(fileHeader));
        file.write(reinterpret_cast<const char*>(&infoHeader), sizeof(infoHeader));

        // 픽셀 데이터 쓰기 (BMP는 아래→위 순서, BGR 순서!)
        uint8_t pad[3] = {0, 0, 0};  // 패딩용 제로 바이트
        for (int y = height_ - 1; y >= 0; --y) {
            for (int x = 0; x < width_; ++x) {
                Pixel p = getPixel(x, y);
                // BMP는 BGR 순서! RGB가 아닙니다!
                uint8_t bgr[3] = {p.b, p.g, p.r};
                file.write(reinterpret_cast<const char*>(bgr), 3);
            }
            if (padding > 0) {
                file.write(reinterpret_cast<const char*>(pad), padding);
            }
        }
        return true;
    }

    // BMP 파일 읽기 — C#의 new Bitmap("file.bmp")과 같습니다
    static Image loadBMP(const std::string& filename) {
        // 파일을 바이너리로 읽는 것은 C#의 BinaryReader와 같습니다
        std::ifstream file(filename, std::ios::binary);
        if (!file) {
            std::cerr << "  [오류] 파일을 열 수 없습니다: " << filename << "\n";
            return Image(0, 0);
        }

        BMPFileHeader fileHeader;
        BMPInfoHeader infoHeader;

        // reinterpret_cast로 구조체에 바이트를 직접 읽어들입니다
        file.read(reinterpret_cast<char*>(&fileHeader), sizeof(fileHeader));
        file.read(reinterpret_cast<char*>(&infoHeader), sizeof(infoHeader));

        // 매직 넘버 확인 — BMP 파일이 맞는지 검증
        if (fileHeader.type != 0x4D42) {
            std::cerr << "  [오류] BMP 파일이 아닙니다!\n";
            return Image(0, 0);
        }

        int w = infoHeader.width;
        int h = std::abs(infoHeader.height);  // 음수일 수 있음 (위→아래 저장)
        Image img(w, h);

        // 픽셀 데이터 위치로 이동
        file.seekg(fileHeader.offset, std::ios::beg);

        int rowSize = w * 3;
        int padding = (4 - (rowSize % 4)) % 4;

        // 아래→위 순서로 읽기 (BMP 표준)
        bool bottomUp = (infoHeader.height > 0);
        for (int row = 0; row < h; ++row) {
            int y = bottomUp ? (h - 1 - row) : row;
            for (int x = 0; x < w; ++x) {
                uint8_t bgr[3];
                file.read(reinterpret_cast<char*>(bgr), 3);
                // BGR → RGB 변환
                img.setPixel(x, y, {bgr[2], bgr[1], bgr[0]});
            }
            // 패딩 건너뛰기
            file.seekg(padding, std::ios::cur);
        }
        return img;
    }

    // ────────────────────────────────────────────
    //  이미지 필터들
    // ────────────────────────────────────────────

    // 그레이스케일(흑백) 변환 — 컬러 사진을 흑백으로 만들기
    // 사람의 눈은 초록색을 가장 밝게 느끼므로, 단순 평균이 아니라
    // 가중 평균을 사용합니다 (ITU-R BT.601 표준)
    Image toGrayscale() const {
        Image result(width_, height_);
        for (int i = 0; i < width_ * height_; ++i) {
            int idx = i * 3;
            // 가중 평균: 빨강 30% + 초록 59% + 파랑 11%
            // 이것은 포토샵의 "Desaturate"와 같은 공식입니다
            uint8_t gray = static_cast<uint8_t>(
                0.299 * data_[idx] + 0.587 * data_[idx + 1] + 0.114 * data_[idx + 2]
            );
            result.data_[idx] = gray;
            result.data_[idx + 1] = gray;
            result.data_[idx + 2] = gray;
        }
        return result;
    }

    // 밝기 조절 — 모든 픽셀을 밝게 또는 어둡게
    // delta: -255 ~ +255 (음수=어둡게, 양수=밝게)
    // C#에서 foreach (var pixel in pixels) { pixel.R += delta; } 와 같은 원리
    Image adjustBrightness(int delta) const {
        Image result(width_, height_);
        for (size_t i = 0; i < data_.size(); ++i) {
            // std::clamp는 C#의 Math.Clamp()와 같습니다 — 값을 범위 안에 가둡니다
            result.data_[i] = static_cast<uint8_t>(
                std::clamp(static_cast<int>(data_[i]) + delta, 0, 255)
            );
        }
        return result;
    }

    // 대비(콘트라스트) 조절 — 밝은 건 더 밝게, 어두운 건 더 어둡게
    // factor: 0.0 = 회색 한 덩어리, 1.0 = 변화 없음, 2.0 = 대비 2배
    Image adjustContrast(float factor) const {
        Image result(width_, height_);
        for (size_t i = 0; i < data_.size(); ++i) {
            // 128(중간값)을 기준으로 멀리 밀거나 당기는 원리
            float val = 128.0f + factor * (static_cast<float>(data_[i]) - 128.0f);
            result.data_[i] = static_cast<uint8_t>(std::clamp(val, 0.0f, 255.0f));
        }
        return result;
    }

    // ────────────────────────────────────────────
    //  커널(Kernel) 기반 필터
    // ────────────────────────────────────────────
    //
    //  커널 연산(convolution)은 포토샵의 필터가 내부적으로 하는 계산입니다
    //
    //  3×3 커널이 이미지 위를 슬라이딩하면서 각 픽셀의 새 값을 계산합니다:
    //
    //  이미지 (5×5 중 일부):          커널 (3×3):
    //  ┌───┬───┬───┬───┬───┐         ┌────┬────┬────┐
    //  │ A │ B │ C │ D │ E │         │ k₁ │ k₂ │ k₃ │
    //  ├───┼───┼───┼───┼───┤         ├────┼────┼────┤
    //  │ F │[G]│[H]│[I]│ J │         │ k₄ │ k₅ │ k₆ │
    //  ├───┼───┼───┼───┼───┤         ├────┼────┼────┤
    //  │ K │[L]│[M]│[N]│ O │         │ k₇ │ k₈ │ k₉ │
    //  ├───┼───┼───┼───┼───┤         └────┴────┴────┘
    //  │ P │[Q]│[R]│[S]│ T │
    //  ├───┼───┼───┼───┼───┤
    //  │ U │ V │ W │ X │ Y │
    //  └───┴───┴───┴───┴───┘
    //
    //  M의 새 값 = G×k₁ + H×k₂ + I×k₃
    //            + L×k₄ + M×k₅ + N×k₆
    //            + Q×k₇ + R×k₈ + S×k₉
    //
    //  이 계산을 모든 픽셀에 대해 반복합니다!
    //

    // 3×3 커널 적용 — 범용 컨볼루션 함수
    // C#에서는 System.Drawing에 이런 기능이 없어서 직접 만들어야 합니다
    Image applyKernel3x3(const std::array<float, 9>& kernel) const {
        Image result(width_, height_);

        for (int y = 0; y < height_; ++y) {
            for (int x = 0; x < width_; ++x) {
                float sumR = 0, sumG = 0, sumB = 0;
                int ki = 0;

                // 3×3 이웃 픽셀을 순회합니다
                for (int ky = -1; ky <= 1; ++ky) {
                    for (int kx = -1; kx <= 1; ++kx) {
                        // 경계 처리: 범위 밖이면 가장자리 픽셀을 반복 사용
                        int nx = std::clamp(x + kx, 0, width_ - 1);
                        int ny = std::clamp(y + ky, 0, height_ - 1);
                        Pixel p = getPixel(nx, ny);

                        sumR += p.r * kernel[ki];
                        sumG += p.g * kernel[ki];
                        sumB += p.b * kernel[ki];
                        ++ki;
                    }
                }

                result.setPixel(x, y, {
                    static_cast<uint8_t>(std::clamp(sumR, 0.0f, 255.0f)),
                    static_cast<uint8_t>(std::clamp(sumG, 0.0f, 255.0f)),
                    static_cast<uint8_t>(std::clamp(sumB, 0.0f, 255.0f))
                });
            }
        }
        return result;
    }

    // 블러(흐림) 필터 — 박스 블러 (Box Blur)
    // 주변 9개 픽셀의 평균을 구합니다 (모든 가중치가 1/9)
    // 포토샵의 "블러" 효과와 같습니다
    Image blur() const {
        // 박스 블러 커널: 모든 값이 1/9 (평균)
        std::array<float, 9> kernel = {
            1.0f/9, 1.0f/9, 1.0f/9,
            1.0f/9, 1.0f/9, 1.0f/9,
            1.0f/9, 1.0f/9, 1.0f/9
        };
        return applyKernel3x3(kernel);
    }

    // 샤픈(선명하게) 필터 — 흐린 사진을 선명하게
    // 중앙 픽셀을 강조하고 주변을 빼는 원리입니다
    Image sharpen() const {
        std::array<float, 9> kernel = {
             0, -1,  0,
            -1,  5, -1,
             0, -1,  0
        };
        return applyKernel3x3(kernel);
    }

    // 엣지 검출 — 소벨(Sobel) 필터
    // 물체의 윤곽선을 찾습니다 — 자율주행차가 차선을 인식하는 기초 기술!
    //
    // X방향 소벨:     Y방향 소벨:
    // ┌────┬────┬────┐  ┌────┬────┬────┐
    // │ -1 │  0 │ +1 │  │ -1 │ -2 │ -1 │
    // ├────┼────┼────┤  ├────┼────┼────┤
    // │ -2 │  0 │ +2 │  │  0 │  0 │  0 │
    // ├────┼────┼────┤  ├────┼────┼────┤
    // │ -1 │  0 │ +1 │  │ +1 │ +2 │ +1 │
    // └────┴────┴────┘  └────┴────┴────┘
    //
    // 최종 결과 = sqrt(X² + Y²) — 피타고라스 정리!
    Image edgeDetectSobel() const {
        // 먼저 그레이스케일로 변환 (엣지 검출은 밝기 변화를 찾으므로)
        Image gray = toGrayscale();
        Image result(width_, height_);

        std::array<float, 9> sobelX = {
            -1, 0, 1,
            -2, 0, 2,
            -1, 0, 1
        };
        std::array<float, 9> sobelY = {
            -1, -2, -1,
             0,  0,  0,
             1,  2,  1
        };

        for (int y = 0; y < height_; ++y) {
            for (int x = 0; x < width_; ++x) {
                float gx = 0, gy = 0;
                int ki = 0;
                for (int ky = -1; ky <= 1; ++ky) {
                    for (int kx = -1; kx <= 1; ++kx) {
                        int nx = std::clamp(x + kx, 0, width_ - 1);
                        int ny = std::clamp(y + ky, 0, height_ - 1);
                        float val = gray.getPixel(nx, ny).r;  // 그레이스케일이라 R=G=B
                        gx += val * sobelX[ki];
                        gy += val * sobelY[ki];
                        ++ki;
                    }
                }
                // 기울기 크기 = sqrt(gx² + gy²)
                uint8_t magnitude = static_cast<uint8_t>(
                    std::clamp(std::sqrt(gx * gx + gy * gy), 0.0f, 255.0f)
                );
                result.setPixel(x, y, {magnitude, magnitude, magnitude});
            }
        }
        return result;
    }

    // ────────────────────────────────────────────
    //  이미지 변환 (Transformations)
    // ────────────────────────────────────────────

    // 좌우 뒤집기 — 거울에 비친 것처럼
    // C#의 Bitmap.RotateFlip(RotateFlipType.RotateNoneFlipX)와 같습니다
    Image flipHorizontal() const {
        Image result(width_, height_);
        for (int y = 0; y < height_; ++y) {
            for (int x = 0; x < width_; ++x) {
                result.setPixel(width_ - 1 - x, y, getPixel(x, y));
            }
        }
        return result;
    }

    // 상하 뒤집기 — 위아래를 뒤집기
    Image flipVertical() const {
        Image result(width_, height_);
        for (int y = 0; y < height_; ++y) {
            for (int x = 0; x < width_; ++x) {
                result.setPixel(x, height_ - 1 - y, getPixel(x, y));
            }
        }
        return result;
    }

    // 90도 시계방향 회전
    // 원래 (x, y) → 새 (height-1-y, x)
    // 가로세로가 바뀝니다!
    Image rotate90CW() const {
        Image result(height_, width_);  // 가로↔세로 교환!
        for (int y = 0; y < height_; ++y) {
            for (int x = 0; x < width_; ++x) {
                result.setPixel(height_ - 1 - y, x, getPixel(x, y));
            }
        }
        return result;
    }

    // 자르기 (Crop) — 이미지의 일부분만 잘라내기
    // C#의 Bitmap.Clone(new Rectangle(...))과 같습니다
    Image crop(int startX, int startY, int cropW, int cropH) const {
        // 범위 보정 — 이미지 밖으로 나가지 않도록
        cropW = std::min(cropW, width_ - startX);
        cropH = std::min(cropH, height_ - startY);
        if (cropW <= 0 || cropH <= 0) return Image(0, 0);

        Image result(cropW, cropH);
        for (int y = 0; y < cropH; ++y) {
            for (int x = 0; x < cropW; ++x) {
                result.setPixel(x, y, getPixel(startX + x, startY + y));
            }
        }
        return result;
    }

    // 크기 변경 (Resize) — 최근접 이웃 보간법 (Nearest Neighbor)
    // 가장 간단한 리사이즈 방법: 새 좌표에서 가장 가까운 원본 픽셀을 복사
    // 빠르지만 계단 현상(aliasing)이 생깁니다
    // C#의 Graphics.InterpolationMode = NearestNeighbor와 같습니다
    Image resize(int newW, int newH) const {
        if (newW <= 0 || newH <= 0) return Image(0, 0);
        Image result(newW, newH);

        // 비율 계산: 새 이미지의 1픽셀이 원본의 몇 픽셀에 해당하는지
        float xRatio = static_cast<float>(width_) / newW;
        float yRatio = static_cast<float>(height_) / newH;

        for (int y = 0; y < newH; ++y) {
            for (int x = 0; x < newW; ++x) {
                // 새 좌표 → 원본 좌표로 역매핑
                int srcX = static_cast<int>(x * xRatio);
                int srcY = static_cast<int>(y * yRatio);
                srcX = std::min(srcX, width_ - 1);
                srcY = std::min(srcY, height_ - 1);
                result.setPixel(x, y, getPixel(srcX, srcY));
            }
        }
        return result;
    }

    // ────────────────────────────────────────────
    //  히스토그램 (Histogram)
    // ────────────────────────────────────────────
    //  히스토그램은 각 밝기 값(0~255)이 몇 개의 픽셀에 나타나는지 세는 것입니다
    //  카메라 앱에서 보이는 그래프가 바로 이것입니다!

    struct Histogram {
        std::array<int, 256> r{};    // 빨강 채널 히스토그램
        std::array<int, 256> g{};    // 초록 채널 히스토그램
        std::array<int, 256> b{};    // 파랑 채널 히스토그램
        std::array<int, 256> lum{};  // 밝기(luminance) 히스토그램
    };

    Histogram computeHistogram() const {
        Histogram hist;
        // 모든 배열을 0으로 초기화 — C#의 new int[256]과 같습니다 (자동 0 초기화)
        hist.r.fill(0);
        hist.g.fill(0);
        hist.b.fill(0);
        hist.lum.fill(0);

        for (int i = 0; i < width_ * height_; ++i) {
            int idx = i * 3;
            uint8_t rv = data_[idx];
            uint8_t gv = data_[idx + 1];
            uint8_t bv = data_[idx + 2];

            hist.r[rv]++;
            hist.g[gv]++;
            hist.b[bv]++;

            // 밝기 계산 (그레이스케일 공식과 동일)
            uint8_t lum = static_cast<uint8_t>(0.299 * rv + 0.587 * gv + 0.114 * bv);
            hist.lum[lum]++;
        }
        return hist;
    }

    // 히스토그램을 콘솔에 ASCII 막대그래프로 출력
    static void printHistogram(const std::array<int, 256>& hist, const std::string& label) {
        // 최대값 찾기 (막대 길이 정규화용)
        int maxVal = *std::max_element(hist.begin(), hist.end());
        if (maxVal == 0) return;

        std::cout << "  [" << label << " 히스토그램] (16구간으로 요약)\n";
        // 256개를 16개 구간으로 묶어서 보여줍니다
        for (int i = 0; i < 16; ++i) {
            int sum = 0;
            for (int j = i * 16; j < (i + 1) * 16; ++j) {
                sum += hist[j];
            }
            int barLen = static_cast<int>(40.0 * sum / (maxVal * 16));
            barLen = std::min(barLen, 40);

            std::cout << "  " << std::setw(3) << (i * 16) << "-"
                      << std::setw(3) << ((i + 1) * 16 - 1) << " |";
            for (int k = 0; k < barLen; ++k) std::cout << "#";
            std::cout << " (" << sum << ")\n";
        }
    }

    // 히스토그램 통계 분석
    static void analyzeHistogram(const std::array<int, 256>& hist, const std::string& label) {
        long long total = 0;
        long long weightedSum = 0;
        int minVal = 255, maxVal = 0;

        for (int i = 0; i < 256; ++i) {
            total += hist[i];
            weightedSum += static_cast<long long>(i) * hist[i];
            if (hist[i] > 0) {
                minVal = std::min(minVal, i);
                maxVal = std::max(maxVal, i);
            }
        }

        double mean = (total > 0) ? static_cast<double>(weightedSum) / total : 0;

        // 표준편차 계산 — 값들이 평균에서 얼마나 퍼져있는지
        double variance = 0;
        for (int i = 0; i < 256; ++i) {
            double diff = i - mean;
            variance += diff * diff * hist[i];
        }
        double stdDev = (total > 0) ? std::sqrt(variance / total) : 0;

        std::cout << "  [" << label << " 통계] 최소=" << minVal
                  << " 최대=" << maxVal
                  << " 평균=" << std::fixed << std::setprecision(1) << mean
                  << " 표준편차=" << stdDev << "\n";
    }
};

// ============================================================================
//  색상 공간 변환: RGB ↔ HSV
// ============================================================================
//  RGB: 컴퓨터가 좋아하는 방식 (빨강, 초록, 파랑 혼합)
//  HSV: 사람이 이해하기 쉬운 방식 (색상, 채도, 밝기)
//  포토샵에서 "색조/채도" 조절할 때 HSV를 사용합니다

// RGB → HSV 변환
HSV rgbToHsv(const Pixel& p) {
    float r = p.r / 255.0f;
    float g = p.g / 255.0f;
    float b = p.b / 255.0f;

    float maxC = std::max({r, g, b});
    float minC = std::min({r, g, b});
    float diff = maxC - minC;

    HSV hsv;
    hsv.v = maxC;  // 명도 = 가장 밝은 채널

    if (diff < 0.00001f) {
        hsv.h = 0;  // 무채색 (회색)
        hsv.s = 0;
        return hsv;
    }

    hsv.s = diff / maxC;  // 채도

    // 색상(Hue) 계산 — 색상환에서의 각도 (0~360)
    if (maxC == r) {
        hsv.h = 60.0f * std::fmod((g - b) / diff, 6.0f);
    } else if (maxC == g) {
        hsv.h = 60.0f * ((b - r) / diff + 2.0f);
    } else {
        hsv.h = 60.0f * ((r - g) / diff + 4.0f);
    }
    if (hsv.h < 0) hsv.h += 360.0f;

    return hsv;
}

// HSV → RGB 변환
Pixel hsvToRgb(const HSV& hsv) {
    float c = hsv.v * hsv.s;        // 채도 × 명도
    float x = c * (1.0f - std::fabs(std::fmod(hsv.h / 60.0f, 2.0f) - 1.0f));
    float m = hsv.v - c;

    float r1 = 0, g1 = 0, b1 = 0;

    // 색상환의 6개 섹터에 따라 RGB 결정
    if (hsv.h < 60)       { r1 = c; g1 = x; b1 = 0; }
    else if (hsv.h < 120) { r1 = x; g1 = c; b1 = 0; }
    else if (hsv.h < 180) { r1 = 0; g1 = c; b1 = x; }
    else if (hsv.h < 240) { r1 = 0; g1 = x; b1 = c; }
    else if (hsv.h < 300) { r1 = x; g1 = 0; b1 = c; }
    else                  { r1 = c; g1 = 0; b1 = x; }

    return {
        static_cast<uint8_t>((r1 + m) * 255),
        static_cast<uint8_t>((g1 + m) * 255),
        static_cast<uint8_t>((b1 + m) * 255)
    };
}

// ============================================================================
//  테스트 이미지 생성 (절차적 생성)
// ============================================================================
//  실제 파일이 없어도 테스트할 수 있도록, 코드로 이미지를 만듭니다
//  게임에서 "프로시저럴 텍스처"라고 부르는 기법입니다

// 그라데이션 이미지 — 왼쪽에서 오른쪽으로 색이 변합니다
// CSS의 linear-gradient와 같은 개념입니다
Image generateGradient(int w, int h) {
    Image img(w, h);
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            // x 비율에 따라 빨강→파랑 그라데이션
            float xr = static_cast<float>(x) / (w - 1);
            float yr = static_cast<float>(y) / (h - 1);
            uint8_t r = static_cast<uint8_t>(255 * xr);       // 오른쪽으로 갈수록 빨강
            uint8_t g = static_cast<uint8_t>(255 * yr);       // 아래로 갈수록 초록
            uint8_t b = static_cast<uint8_t>(255 * (1 - xr)); // 왼쪽으로 갈수록 파랑
            img.setPixel(x, y, {r, g, b});
        }
    }
    return img;
}

// 체커보드 패턴 — 체스판처럼 검정/하양이 번갈아 나옵니다
Image generateCheckerboard(int w, int h, int cellSize) {
    Image img(w, h);
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            // 정수 나눗셈으로 어떤 칸인지 결정
            // 짝수 칸 = 하양, 홀수 칸 = 빨강
            bool isWhite = ((x / cellSize) + (y / cellSize)) % 2 == 0;
            if (isWhite) {
                img.setPixel(x, y, {240, 240, 240});
            } else {
                img.setPixel(x, y, {200, 50, 50});
            }
        }
    }
    return img;
}

// 원과 도형이 있는 테스트 이미지 — 필터 테스트에 적합
Image generateTestScene(int w, int h) {
    Image img(w, h);

    // 배경: 부드러운 파란색 그라데이션 (하늘처럼)
    for (int y = 0; y < h; ++y) {
        uint8_t skyBlue = static_cast<uint8_t>(180 + 75.0 * y / h);
        for (int x = 0; x < w; ++x) {
            img.setPixel(x, y, {100, 150, skyBlue});
        }
    }

    // 원 그리기 — 원의 방정식: (x-cx)² + (y-cy)² ≤ r²
    int cx = w / 3, cy = h / 3, radius = std::min(w, h) / 5;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            int dx = x - cx, dy = y - cy;
            if (dx * dx + dy * dy <= radius * radius) {
                img.setPixel(x, y, {255, 200, 50});  // 노란 원 (태양)
            }
        }
    }

    // 사각형 그리기
    int rx = w / 2, ry = h / 2, rw = w / 4, rh = h / 4;
    for (int y = ry; y < std::min(ry + rh, h); ++y) {
        for (int x = rx; x < std::min(rx + rw, w); ++x) {
            img.setPixel(x, y, {50, 180, 50});  // 초록 사각형
        }
    }

    // 대각선 줄무늬 — 엣지 검출 테스트에 좋습니다
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if ((x + y) % 40 < 3) {
                img.setPixel(x, y, {255, 255, 255});  // 흰색 대각선
            }
        }
    }

    return img;
}

// ============================================================================
//  성능 측정 유틸리티
// ============================================================================
// C#의 Stopwatch와 같은 역할입니다
// chrono는 C++의 시간 측정 라이브러리입니다

class Timer {
    std::chrono::high_resolution_clock::time_point start_;
    std::string label_;
public:
    Timer(const std::string& label) : label_(label) {
        start_ = std::chrono::high_resolution_clock::now();
    }
    ~Timer() {
        auto end = std::chrono::high_resolution_clock::now();
        auto ms = std::chrono::duration_cast<std::chrono::microseconds>(end - start_).count();
        std::cout << "  [성능] " << label_ << ": "
                  << ms / 1000.0 << " ms\n";
    }
};

// ============================================================================
//  데모 실행 함수들
// ============================================================================

// 1단계: 테스트 이미지 생성 데모
void demoImageGeneration() {
    std::cout << "\n========================================\n";
    std::cout << " 1단계: 테스트 이미지 절차적 생성\n";
    std::cout << "========================================\n";

    std::cout << "  그라데이션 이미지 (256x256) 생성 중...\n";
    Image gradient = generateGradient(256, 256);
    gradient.saveBMP("test_gradient.bmp");
    std::cout << "  -> test_gradient.bmp 저장 완료\n";

    std::cout << "  체커보드 이미지 (256x256, 셀=32) 생성 중...\n";
    Image checker = generateCheckerboard(256, 256, 32);
    checker.saveBMP("test_checkerboard.bmp");
    std::cout << "  -> test_checkerboard.bmp 저장 완료\n";

    std::cout << "  테스트 장면 이미지 (320x240) 생성 중...\n";
    Image scene = generateTestScene(320, 240);
    scene.saveBMP("test_scene.bmp");
    std::cout << "  -> test_scene.bmp 저장 완료\n";
}

// 2단계: BMP 읽기/쓰기 검증
void demoBMPReadWrite() {
    std::cout << "\n========================================\n";
    std::cout << " 2단계: BMP 파일 읽기/쓰기 검증\n";
    std::cout << "========================================\n";

    // 원본 생성 → 저장 → 다시 읽기 → 다시 저장
    Image original = generateGradient(100, 80);
    original.saveBMP("bmp_test_original.bmp");

    Image loaded = Image::loadBMP("bmp_test_original.bmp");
    std::cout << "  읽어온 이미지: " << loaded.width() << "x" << loaded.height() << "\n";

    // 몇 개 픽셀 비교하여 정확성 검증
    bool match = true;
    for (int y = 0; y < 80 && match; y += 20) {
        for (int x = 0; x < 100 && match; x += 25) {
            Pixel orig = original.getPixel(x, y);
            Pixel read = loaded.getPixel(x, y);
            if (orig.r != read.r || orig.g != read.g || orig.b != read.b) {
                std::cout << "  [불일치] (" << x << "," << y << ") "
                          << "원본=(" << (int)orig.r << "," << (int)orig.g << "," << (int)orig.b << ") "
                          << "읽기=(" << (int)read.r << "," << (int)read.g << "," << (int)read.b << ")\n";
                match = false;
            }
        }
    }
    if (match) {
        std::cout << "  [성공] BMP 읽기/쓰기 검증 통과! 모든 샘플 픽셀 일치\n";
    }

    // 다시 저장해서 파일 크기 비교
    loaded.saveBMP("bmp_test_reload.bmp");
    std::cout << "  -> bmp_test_reload.bmp 저장 완료 (동일해야 합니다)\n";
}

// 3단계: 이미지 필터 데모
void demoFilters() {
    std::cout << "\n========================================\n";
    std::cout << " 3단계: 이미지 필터 적용\n";
    std::cout << "========================================\n";

    Image scene = generateTestScene(320, 240);

    // 그레이스케일
    {
        Timer t("그레이스케일 변환 (320x240)");
        Image gray = scene.toGrayscale();
        gray.saveBMP("filter_grayscale.bmp");
    }
    std::cout << "  -> filter_grayscale.bmp 저장\n";

    // 밝기 +50
    {
        Timer t("밝기 +50 (320x240)");
        Image bright = scene.adjustBrightness(50);
        bright.saveBMP("filter_bright.bmp");
    }
    std::cout << "  -> filter_bright.bmp 저장\n";

    // 밝기 -50
    {
        Timer t("밝기 -50 (320x240)");
        Image dark = scene.adjustBrightness(-50);
        dark.saveBMP("filter_dark.bmp");
    }
    std::cout << "  -> filter_dark.bmp 저장\n";

    // 대비 1.5배
    {
        Timer t("대비 x1.5 (320x240)");
        Image contrast = scene.adjustContrast(1.5f);
        contrast.saveBMP("filter_contrast.bmp");
    }
    std::cout << "  -> filter_contrast.bmp 저장\n";

    // 블러
    {
        Timer t("박스 블러 (320x240)");
        Image blurred = scene.blur();
        blurred.saveBMP("filter_blur.bmp");
    }
    std::cout << "  -> filter_blur.bmp 저장\n";

    // 샤픈
    {
        Timer t("샤픈 (320x240)");
        Image sharp = scene.sharpen();
        sharp.saveBMP("filter_sharpen.bmp");
    }
    std::cout << "  -> filter_sharpen.bmp 저장\n";

    // 소벨 엣지 검출
    {
        Timer t("소벨 엣지 검출 (320x240)");
        Image edges = scene.edgeDetectSobel();
        edges.saveBMP("filter_edges.bmp");
    }
    std::cout << "  -> filter_edges.bmp 저장\n";
}

// 4단계: 이미지 변환 데모
void demoTransformations() {
    std::cout << "\n========================================\n";
    std::cout << " 4단계: 이미지 변환 (Transformations)\n";
    std::cout << "========================================\n";

    Image scene = generateTestScene(320, 240);

    // 좌우 뒤집기
    {
        Timer t("좌우 뒤집기 (320x240)");
        Image flipped = scene.flipHorizontal();
        flipped.saveBMP("transform_flip_h.bmp");
    }
    std::cout << "  -> transform_flip_h.bmp 저장\n";

    // 상하 뒤집기
    {
        Timer t("상하 뒤집기 (320x240)");
        Image flipped = scene.flipVertical();
        flipped.saveBMP("transform_flip_v.bmp");
    }
    std::cout << "  -> transform_flip_v.bmp 저장\n";

    // 90도 회전
    {
        Timer t("90도 회전 (320x240 -> 240x320)");
        Image rotated = scene.rotate90CW();
        rotated.saveBMP("transform_rotate90.bmp");
        std::cout << "  회전 후 크기: " << rotated.width() << "x" << rotated.height() << "\n";
    }
    std::cout << "  -> transform_rotate90.bmp 저장\n";

    // 자르기 (Crop)
    {
        Timer t("자르기 (100x100 영역)");
        Image cropped = scene.crop(50, 30, 100, 100);
        cropped.saveBMP("transform_crop.bmp");
        std::cout << "  잘라낸 크기: " << cropped.width() << "x" << cropped.height() << "\n";
    }
    std::cout << "  -> transform_crop.bmp 저장\n";

    // 리사이즈 (확대)
    {
        Timer t("리사이즈 640x480 (2배 확대)");
        Image bigger = scene.resize(640, 480);
        bigger.saveBMP("transform_resize_up.bmp");
    }
    std::cout << "  -> transform_resize_up.bmp 저장\n";

    // 리사이즈 (축소)
    {
        Timer t("리사이즈 160x120 (절반 축소)");
        Image smaller = scene.resize(160, 120);
        smaller.saveBMP("transform_resize_down.bmp");
    }
    std::cout << "  -> transform_resize_down.bmp 저장\n";
}

// 5단계: 히스토그램 분석
void demoHistogram() {
    std::cout << "\n========================================\n";
    std::cout << " 5단계: 히스토그램 분석\n";
    std::cout << "========================================\n";

    Image scene = generateTestScene(320, 240);
    Image::Histogram hist = scene.computeHistogram();

    // 밝기 히스토그램 출력
    Image::printHistogram(hist.lum, "밝기");
    std::cout << "\n";
    Image::analyzeHistogram(hist.lum, "밝기");
    Image::analyzeHistogram(hist.r, "빨강(R)");
    Image::analyzeHistogram(hist.g, "초록(G)");
    Image::analyzeHistogram(hist.b, "파랑(B)");

    // 그레이스케일 변환 후 히스토그램 비교
    std::cout << "\n  --- 그레이스케일 변환 후 ---\n";
    Image gray = scene.toGrayscale();
    Image::Histogram grayHist = gray.computeHistogram();
    Image::printHistogram(grayHist.lum, "그레이스케일 밝기");
    Image::analyzeHistogram(grayHist.lum, "그레이스케일 밝기");
}

// 6단계: RGB ↔ HSV 변환 데모
void demoColorSpace() {
    std::cout << "\n========================================\n";
    std::cout << " 6단계: 색상 공간 변환 (RGB <-> HSV)\n";
    std::cout << "========================================\n";

    // 몇 가지 색상으로 RGB→HSV→RGB 왕복 테스트
    // 정확히 복원되면 변환 함수가 올바른 것입니다
    struct TestColor { const char* name; Pixel pixel; };
    TestColor colors[] = {
        {"빨강",   {255, 0,   0  }},
        {"초록",   {0,   255, 0  }},
        {"파랑",   {0,   0,   255}},
        {"노랑",   {255, 255, 0  }},
        {"시안",   {0,   255, 255}},
        {"마젠타", {255, 0,   255}},
        {"흰색",   {255, 255, 255}},
        {"회색",   {128, 128, 128}},
        {"주황",   {255, 165, 0  }},
    };

    std::cout << "  RGB -> HSV -> RGB 왕복 변환 테스트:\n";
    std::cout << "  " << std::setw(8) << "색상" << " | "
              << std::setw(15) << "원본 RGB" << " | "
              << std::setw(22) << "HSV" << " | "
              << std::setw(15) << "복원 RGB" << " | 일치?\n";
    std::cout << "  " << std::string(75, '-') << "\n";

    for (const auto& tc : colors) {
        HSV hsv = rgbToHsv(tc.pixel);
        Pixel back = hsvToRgb(hsv);

        bool match = (std::abs(tc.pixel.r - back.r) <= 1) &&
                     (std::abs(tc.pixel.g - back.g) <= 1) &&
                     (std::abs(tc.pixel.b - back.b) <= 1);

        std::cout << "  " << std::setw(8) << tc.name << " | "
                  << "(" << std::setw(3) << (int)tc.pixel.r << ","
                  << std::setw(3) << (int)tc.pixel.g << ","
                  << std::setw(3) << (int)tc.pixel.b << ") | "
                  << "H=" << std::setw(5) << std::fixed << std::setprecision(1) << hsv.h
                  << " S=" << std::setprecision(2) << hsv.s
                  << " V=" << hsv.v << " | "
                  << "(" << std::setw(3) << (int)back.r << ","
                  << std::setw(3) << (int)back.g << ","
                  << std::setw(3) << (int)back.b << ") | "
                  << (match ? "OK" : "FAIL") << "\n";
    }

    // HSV를 이용한 색조 변환 이미지 생성
    std::cout << "\n  색조(Hue) 회전 데모: 원본 이미지의 색을 120도 회전...\n";
    Image scene = generateTestScene(160, 120);
    Image hueShifted(160, 120);

    for (int y = 0; y < 120; ++y) {
        for (int x = 0; x < 160; ++x) {
            Pixel p = scene.getPixel(x, y);
            HSV hsv = rgbToHsv(p);
            hsv.h = std::fmod(hsv.h + 120.0f, 360.0f);  // 120도 회전
            Pixel shifted = hsvToRgb(hsv);
            hueShifted.setPixel(x, y, shifted);
        }
    }
    hueShifted.saveBMP("colorspace_hue_shifted.bmp");
    std::cout << "  -> colorspace_hue_shifted.bmp 저장\n";
}

// 7단계: 성능 벤치마크 — 100만 픽셀 처리
void demoPerformance() {
    std::cout << "\n========================================\n";
    std::cout << " 7단계: 성능 벤치마크 (100만 픽셀)\n";
    std::cout << "========================================\n";

    // 1000 × 1000 = 1,000,000 픽셀 이미지 생성
    // 이것이 C++이 이미지 처리에 강한 이유를 보여줍니다!
    const int SIZE = 1000;
    std::cout << "  이미지 크기: " << SIZE << "x" << SIZE
              << " (" << SIZE * SIZE << " 픽셀 = 약 "
              << SIZE * SIZE * 3 / 1024 << " KB)\n\n";

    Image bigImage = generateTestScene(SIZE, SIZE);

    // 각 필터의 처리 시간 측정
    // C#에서 같은 작업을 하면 GC(가비지 컬렉션)와 bounds checking으로
    // 보통 2~5배 느립니다. C++은 이런 오버헤드가 없습니다!

    {
        Timer t("그레이스케일 (100만 픽셀)");
        Image result = bigImage.toGrayscale();
    }

    {
        Timer t("밝기 조절 (100만 픽셀)");
        Image result = bigImage.adjustBrightness(30);
    }

    {
        Timer t("대비 조절 (100만 픽셀)");
        Image result = bigImage.adjustContrast(1.5f);
    }

    {
        Timer t("박스 블러 (100만 픽셀) — 커널 컨볼루션");
        Image result = bigImage.blur();
    }

    {
        Timer t("샤픈 (100만 픽셀) — 커널 컨볼루션");
        Image result = bigImage.sharpen();
    }

    {
        Timer t("소벨 엣지 검출 (100만 픽셀) — 가장 무거운 연산");
        Image result = bigImage.edgeDetectSobel();
    }

    {
        Timer t("좌우 뒤집기 (100만 픽셀)");
        Image result = bigImage.flipHorizontal();
    }

    {
        Timer t("90도 회전 (100만 픽셀)");
        Image result = bigImage.rotate90CW();
    }

    {
        Timer t("리사이즈 500x500 (100만 → 25만 픽셀)");
        Image result = bigImage.resize(500, 500);
    }

    {
        Timer t("리사이즈 2000x2000 (100만 → 400만 픽셀)");
        Image result = bigImage.resize(2000, 2000);
    }

    {
        Timer t("히스토그램 계산 (100만 픽셀)");
        Image::Histogram hist = bigImage.computeHistogram();
    }

    {
        Timer t("RGB→HSV 변환 (100만 픽셀)");
        // 포인터를 직접 사용하여 가장 빠른 방식으로 처리
        const uint8_t* data = bigImage.rawData();
        int total = bigImage.totalPixels();
        volatile float dummy = 0;  // 최적화 방지용 — 컴파일러가 계산을 생략하지 못하게
        for (int i = 0; i < total; ++i) {
            int idx = i * 3;
            Pixel p = {data[idx], data[idx + 1], data[idx + 2]};
            HSV hsv = rgbToHsv(p);
            dummy = hsv.h;  // 결과를 사용해야 컴파일러가 최적화로 건너뛰지 않습니다
        }
    }

    std::cout << "\n  [참고] C++이 이미지 처리에 유리한 이유:\n";
    std::cout << "  1. 메모리 직접 접근: 포인터로 픽셀을 바로 조작 (오버헤드 0)\n";
    std::cout << "  2. Boxing/Unboxing 없음: C#의 값타입↔참조타입 변환 비용 없음\n";
    std::cout << "  3. GC 없음: 가비지 컬렉터가 멈추는 일이 없음\n";
    std::cout << "  4. SIMD 활용: -O2 옵션으로 컴파일하면 자동 벡터화\n";
    std::cout << "  5. 캐시 친화적: 연속 메모리 접근 패턴으로 캐시 히트율 극대화\n";
}

// ============================================================================
//  메인 함수
// ============================================================================

/*
=============================================================================
  실행 흐름 가이드 (이미지는 시뮬레이션, 외부 파일 불필요)
=============================================================================
  1. demoImageGeneration:
     200x150 grayscale 이미지 (graystripes.bmp), 그라데이션 패턴
     200x150 RGB 컬러 이미지 (color.bmp), 무지개 패턴
     → 메모리: 200*150 = 30000 픽셀, RGB는 90000 바이트

  2. demoBMPReadWrite:
     write → read → 픽셀 일치 검증 → "Round-trip OK"

  3. demoFilters:
     Blur (3x3 평균): 인접 9픽셀 평균 → 부드러워짐
     Edge (Sobel): 수평/수직 미분 → 윤곽선 검출
     Sharpen: 라플라시안 + 원본 → 선명화
     각 출력 → blur.bmp / edge.bmp / sharpen.bmp

  4. demoTransformations:
     Rotate 90°: (x,y) → (y, w-1-x)
     Flip horizontal: x → w-1-x
     Crop: 부분만 추출

  5. demoHistogram:
     픽셀 값 분포 [0~255] 256bin 카운트
     ASCII 막대그래프로 출력

  6. demoColorSpace:
     RGB → Grayscale (0.299R + 0.587G + 0.114B)
     RGB → HSV 변환 공식 적용

  메모리 패턴:
    - 이미지 = vector<uint8_t> 연속 메모리 (cache-friendly)
    - 필터: 임시 버퍼 1개 + 결과 1개 = 2배 메모리
    - in-place 가능한 연산은 1배 메모리
=============================================================================
*/

int main() {
    std::cout << "============================================================\n";
    std::cout << "   이미지 처리 엔진 (Image Processing Engine)\n";
    std::cout << "   C++로 배우는 컴퓨터 비전의 기초\n";
    std::cout << "============================================================\n";
    std::cout << "   OpenCV, Photoshop 등이 C++을 사용하는 이유를 체험합니다.\n";
    std::cout << "   모든 이미지는 코드로 생성되므로 외부 파일이 필요 없습니다.\n";

    demoImageGeneration();
    demoBMPReadWrite();
    demoFilters();
    demoTransformations();
    demoHistogram();
    demoColorSpace();

    // 7단계: 성능 벤치마크
    demoPerformance();

    std::cout << "\n============================================================\n";
    std::cout << "   모든 데모 완료!\n";
    std::cout << "   생성된 BMP 파일들을 이미지 뷰어로 열어서 확인해보세요.\n";
    std::cout << "============================================================\n";

    return 0;
}
