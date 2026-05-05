// ============================================================================
// 오디오 프로세싱 엔진 (Audio Processing Engine)
// ============================================================================
// C++로 만든 유명한 오디오: Pro Tools, Ableton, FL Studio, VST플러그인, Unreal오디오
// 실시간 오디오에서 GC가 발생하면 '뚝뚝' 끊기는 소리가 납니다 → C++ 필수!
// 1초에 44100번 샘플 계산 (CD 품질), 한 샘플당 약 0.023ms밖에 시간이 없음!
//
//  오디오 신호 흐름:
//  ┌──────────┐   ┌────────┐   ┌──────┐   ┌────────┐
//  │오실레이터│──>│ 이펙트 │──>│ 믹서 │──>│WAV파일 │
//  │ (파형)   │   │(에코등)│   │(합치기)│   │ (저장) │
//  └──────────┘   └────────┘   └──────┘   └────────┘
//
//  샘플값 범위: float 배열 = C#의 float[]와 같습니다. 오디오는 -1.0 ~ 1.0 사이의 실수입니다
//   +1.0 ── ╲  ╱ ╲  ╱ ──  (최대)
//    0.0 ────╲╱───╲╱────  (무음)
//   -1.0 ────────────────  (최소)
// ============================================================================

#include <iostream>
#include <vector>      // C#의 List<float>
#include <cmath>       // sin, cos 등
#include <fstream>     // C#의 FileStream / BinaryWriter
#include <string>
#include <algorithm>   // min, max
#include <cstdint>     // int16_t, uint32_t
#include <random>      // 노이즈용 랜덤
#include <memory>
#include <array>
#include <numeric>

// 상수 - C#의 const와 같습니다
constexpr double PI = 3.14159265358979323846;
constexpr double TWO_PI = 2.0 * PI;
constexpr int SAMPLE_RATE = 44100;  // CD품질: 1초에 44100샘플

// ============================================================================
// 1단계: 오디오 버퍼 - 소리 데이터를 담는 그릇
// ============================================================================
//  인덱스: [0]  [1]  [2]  [3]  [4]  ...
//  샘플값: 0.0  0.3  0.5  0.3  0.0  ...  ← 이 숫자들이 스피커를 진동시킴!
class AudioBuffer {
public:
    std::vector<float> samples;  // C#의 float[]과 같습니다
    int sampleRate;
    int channels;

    AudioBuffer(int sr = SAMPLE_RATE, int ch = 1) : sampleRate(sr), channels(ch) {}
    AudioBuffer(double secs, int sr = SAMPLE_RATE, int ch = 1)
        : sampleRate(sr), channels(ch) {
        samples.resize(static_cast<int>(secs * sr * ch), 0.0f);
    }

    double duration() const { return sampleRate>0 ? double(samples.size())/(sampleRate*channels) : 0; }
    size_t size() const { return samples.size(); }
    float& operator[](size_t i) { return samples[i]; }
    const float& operator[](size_t i) const { return samples[i]; }
    void clear() { std::fill(samples.begin(), samples.end(), 0.0f); }

    // 다른 버퍼를 더하기 (믹싱의 기본!)
    void mixWith(const AudioBuffer& o, float vol = 1.0f) {
        size_t len = std::min(samples.size(), o.samples.size());
        for (size_t i=0; i<len; i++) samples[i] += o.samples[i]*vol;
    }

    float peakLevel() const {
        float pk=0; for (float s:samples) { float a=std::fabs(s); if(a>pk)pk=a; } return pk;
    }

    // 정규화 - 소리가 너무 크거나 작지 않게 맞춤
    void normalize(float target = 0.95f) {
        float pk=peakLevel();
        if (pk>0.0001f) { float sc=target/pk; for (float& s:samples) s*=sc; }
    }

    // ASCII 파형 시각화
    void printWaveform(int w=60, int h=9) const {
        if (samples.empty()) { std::cout<<"  (빈 버퍼)\n"; return; }
        std::cout << "  파형 (+1.0 위, -1.0 아래):" << std::endl;
        int perCol = std::max(1, int(samples.size())/w);
        for (int row=0; row<h; row++) {
            float rv = 1.0f - 2.0f*row/(h-1);
            std::cout << "  ";
            for (int col=0; col<w; col++) {
                int si=col*perCol, ei=std::min(si+perCol, int(samples.size()));
                float sum=0; int cnt=0;
                for (int i=si; i<ei; i++) { sum+=samples[i]; cnt++; }
                float avg = cnt>0 ? sum/cnt : 0;
                float thr = 2.0f/h;
                if (std::fabs(avg-rv)<thr) std::cout<<'#';
                else if (row==h/2) std::cout<<'-';
                else std::cout<<' ';
            }
            std::cout << std::endl;
        }
    }
};

// ============================================================================
// 2단계: 파형 생성기 - 사인파 생성은 C#에서 Math.Sin()을 루프로 도는 것과 같습니다
// ============================================================================
//  사인파(부드러운):  ╱╲  ╱╲     사각파(전자음):  ┌─┐ ┌─┐
//                    ╱  ╲╱  ╲                     │ └─┘ └─
//  톱니파(날카로운):  ╱│ ╱│ ╱│     삼각파(플루트):  ╱╲  ╱╲
//                    ╱ │╱ │╱ │                     ╱  ╲╱  ╲
namespace WaveGen {
    AudioBuffer sine(double freq, double secs, double amp=1.0, int sr=SAMPLE_RATE) {
        AudioBuffer buf(secs, sr);
        for (size_t i=0; i<buf.size(); i++) {
            double t = double(i)/sr;
            buf[i] = float(amp * std::sin(TWO_PI * freq * t));
        }
        return buf;
    }
    AudioBuffer square(double freq, double secs, double amp=1.0, int sr=SAMPLE_RATE) {
        AudioBuffer buf(secs, sr);
        for (size_t i=0; i<buf.size(); i++) {
            double phase = std::fmod(double(i)/sr * freq, 1.0);
            buf[i] = float(amp * (phase<0.5 ? 1.0 : -1.0));
        }
        return buf;
    }
    AudioBuffer sawtooth(double freq, double secs, double amp=1.0, int sr=SAMPLE_RATE) {
        AudioBuffer buf(secs, sr);
        for (size_t i=0; i<buf.size(); i++) {
            double phase = std::fmod(double(i)/sr * freq, 1.0);
            buf[i] = float(amp * (2.0*phase - 1.0));
        }
        return buf;
    }
    AudioBuffer triangle(double freq, double secs, double amp=1.0, int sr=SAMPLE_RATE) {
        AudioBuffer buf(secs, sr);
        for (size_t i=0; i<buf.size(); i++) {
            double phase = std::fmod(double(i)/sr * freq, 1.0);
            buf[i] = float(amp * (4.0*std::fabs(phase-0.5) - 1.0));
        }
        return buf;
    }
    // 백색소음 - 라디오의 "쉬~" 소리, 심벌즈에도 사용
    AudioBuffer whiteNoise(double secs, double amp=1.0, int sr=SAMPLE_RATE) {
        AudioBuffer buf(secs, sr);
        std::random_device rd; std::mt19937 gen(rd());
        std::uniform_real_distribution<float> dist(-1.0f, 1.0f);
        for (size_t i=0; i<buf.size(); i++) buf[i] = float(amp)*dist(gen);
        return buf;
    }
}

// ============================================================================
// 3단계: 오디오 이펙트
// ============================================================================
// 이펙트 체인: 원본 → [볼륨] → [에코] → [필터] → [디스토션] → 최종
namespace Effects {
    // 볼륨 - C#에서 for (int i=0;i<len;i++) buf[i] *= vol; 과 같습니다
    void applyVolume(AudioBuffer& buf, float vol) {
        for (size_t i=0; i<buf.size(); i++) buf[i]*=vol;
    }
    // 페이드 인 - 소리가 점점 커짐 (0% → 100%)
    void fadeIn(AudioBuffer& buf, double secs) {
        int n=std::min(int(secs*buf.sampleRate), int(buf.size()));
        for (int i=0; i<n; i++) buf[i] *= float(i)/n;
    }
    // 페이드 아웃 - 소리가 점점 작아짐 (100% → 0%)
    void fadeOut(AudioBuffer& buf, double secs) {
        int n=std::min(int(secs*buf.sampleRate), int(buf.size()));
        int start=int(buf.size())-n;
        for (int i=start; i<int(buf.size()); i++)
            buf[i] *= float(int(buf.size())-i)/n;
    }
    // 에코/딜레이 - 메아리! 원본 뒤에 작아진 복사본이 반복됨
    //  원본: ████████  에코1: ...████████  에코2: ......████████
    AudioBuffer echo(const AudioBuffer& in, double delay=0.3, float fb=0.5f, int num=3) {
        int ds=int(delay*in.sampleRate);
        AudioBuffer out(0.0, in.sampleRate);
        out.samples.resize(in.size()+ds*num, 0.0f);
        for (size_t i=0; i<in.size(); i++) out[i]=in[i];
        float curFb=fb;
        for (int e=1; e<=num; e++) {
            int off=ds*e;
            for (size_t i=0; i<in.size(); i++)
                if (i+off<out.size()) out[i+off]+=in[i]*curFb;
            curFb*=fb;
        }
        return out;
    }
    // 로우패스 필터 - 높은음을 깎아서 부드럽게
    // 1차 IIR 필터: y[n] = alpha*x[n] + (1-alpha)*y[n-1]
    void lowPassFilter(AudioBuffer& buf, float alpha=0.1f) {
        if (buf.size()<2) return;
        float prev=buf[0];
        for (size_t i=1; i<buf.size(); i++) { buf[i]=alpha*buf[i]+(1-alpha)*prev; prev=buf[i]; }
    }
    // 디스토션 - 일부러 찌그러트리기! 록기타의 "찌직" 소리
    //  사인파 → 클리핑: 둥근 꼭대기가 잘려서 평평해짐
    void distortion(AudioBuffer& buf, float gain=2.0f, float thresh=0.7f) {
        for (size_t i=0; i<buf.size(); i++) {
            float s=buf[i]*gain;
            if (s>thresh) s=thresh; if (s<-thresh) s=-thresh;
            buf[i]=s;
        }
    }
    void reverse(AudioBuffer& buf) { std::reverse(buf.samples.begin(), buf.samples.end()); }
    // 속도 변경 - 빠르면 다람쥐목소리, 느리면 괴물목소리!
    AudioBuffer changeSpeed(const AudioBuffer& in, double factor) {
        int newSz=int(in.size()/factor);
        AudioBuffer out(0.0, in.sampleRate); out.samples.resize(newSz);
        for (int i=0; i<newSz; i++) {
            double si=i*factor; int idx=int(si);
            if (idx>=int(in.size())-1) out[i]=in[in.size()-1];
            else { float f=float(si-idx); out[i]=in[idx]*(1-f)+in[idx+1]*f; } // 선형보간
        }
        return out;
    }
}

// ============================================================================
// 4단계: ADSR 엔벨로프 - 시간에 따른 볼륨 변화
// ============================================================================
//  피아노 건반: 빠르게커짐(A) → 약간줄어듦(D) → 유지(S) → 놓으면사라짐(R)
//  볼륨
//  1.0 │  ╱╲
//      │ ╱  ╲________
//  0.7 │╱            ╲
//  0.0 │______________╲___
//      │ A   D    S    R
struct ADSREnvelope {
    double attack, decay, sustain, release;
    ADSREnvelope(double a=0.01, double d=0.1, double s=0.7, double r=0.2)
        : attack(a), decay(d), sustain(s), release(r) {}

    void apply(AudioBuffer& buf, double noteOn) const {
        int sr=buf.sampleRate;
        int aS=int(attack*sr), dS=int(decay*sr), nS=int(noteOn*sr), rS=int(release*sr);
        for (size_t i=0; i<buf.size(); i++) {
            int s=int(i); float env=0;
            if (s<aS) env=float(s)/aS;                                    // Attack
            else if (s<aS+dS) env=1.0f-float(s-aS)/dS*(1.0f-float(sustain)); // Decay
            else if (s<nS) env=float(sustain);                             // Sustain
            else if (s<nS+rS) env=float(sustain)*(1.0f-float(s-nS)/rS);   // Release
            buf[i]*=env;
        }
    }
};

// ============================================================================
// 5단계: WAV 파일 쓰기 - WAV 파일 쓰기는 C#의 BinaryWriter와 같습니다
// ============================================================================
//  WAV 구조: [RIFF헤더 12B] [fmt청크 24B] [data청크 = 실제오디오]
class WavWriter {
    static void w16(std::ofstream& f, uint16_t v) { f.put(char(v&0xFF)); f.put(char((v>>8)&0xFF)); }
    static void w32(std::ofstream& f, uint32_t v) {
        f.put(char(v&0xFF)); f.put(char((v>>8)&0xFF));
        f.put(char((v>>16)&0xFF)); f.put(char((v>>24)&0xFF));
    }
public:
    static bool save(const std::string& fn, const AudioBuffer& buf) {
        std::ofstream f(fn, std::ios::binary);
        if (!f.is_open()) { std::cerr<<"  [오류] 파일열기실패: "<<fn<<std::endl; return false; }
        int ch=buf.channels, sr=buf.sampleRate, bps=16;
        int dataSize=int(buf.size())*bps/8;
        // RIFF 헤더
        f.write("RIFF",4); w32(f,36+dataSize); f.write("WAVE",4);
        // fmt 청크
        f.write("fmt ",4); w32(f,16); w16(f,1); w16(f,ch);
        w32(f,sr); w32(f,sr*ch*bps/8); w16(f,ch*bps/8); w16(f,bps);
        // data 청크 - float(-1~+1)을 16비트정수(-32768~+32767)로 변환
        f.write("data",4); w32(f,dataSize);
        for (size_t i=0; i<buf.size(); i++) {
            float s=std::max(-1.0f, std::min(1.0f, buf[i]));
            w16(f, uint16_t(int16_t(s*32767.0f)));
        }
        f.close(); return true;
    }
};

// ============================================================================
// 6단계: 신시사이저 - 오실레이터 + ADSR + 이펙트
// ============================================================================
enum class WaveType { SINE, SQUARE, SAWTOOTH, TRIANGLE, NOISE };

// 음이름→주파수 변환 (A4=440Hz, 반음=2^(1/12)배)
namespace Notes {
    double freq(int midi) { return 440.0*std::pow(2.0,(midi-69)/12.0); }
    constexpr int C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72;
}

class Synthesizer {
    WaveType type_; ADSREnvelope env_; double vol_;
public:
    Synthesizer(WaveType t=WaveType::SINE, double v=0.8) : type_(t), vol_(v) {}
    void setEnvelope(double a,double d,double s,double r) { env_={a,d,s,r}; }
    void setWaveType(WaveType t) { type_=t; }
    void setVolume(double v) { vol_=v; }

    AudioBuffer playNote(int midi, double dur, int sr=SAMPLE_RATE) {
        double f=Notes::freq(midi), total=dur+env_.release;
        AudioBuffer buf(0.0,sr);
        switch(type_) {
            case WaveType::SINE:     buf=WaveGen::sine(f,total,vol_,sr); break;
            case WaveType::SQUARE:   buf=WaveGen::square(f,total,vol_,sr); break;
            case WaveType::SAWTOOTH: buf=WaveGen::sawtooth(f,total,vol_,sr); break;
            case WaveType::TRIANGLE: buf=WaveGen::triangle(f,total,vol_,sr); break;
            case WaveType::NOISE:    buf=WaveGen::whiteNoise(total,vol_,sr); break;
        }
        env_.apply(buf, dur);
        return buf;
    }
};

// ============================================================================
// 7단계: 오디오 믹서 - 여러 트랙을 합치기
// ============================================================================
//  트랙1(보컬) ─┐
//  트랙2(기타) ─┼─> [믹서] ──> 최종출력
//  트랙3(드럼) ─┘
struct MixerTrack {
    std::string name; AudioBuffer buffer; float volume;
    MixerTrack(const std::string& n, const AudioBuffer& b, float v=1.0f)
        : name(n), buffer(b), volume(v) {}
};

class AudioMixer {
    std::vector<MixerTrack> tracks_;
    int sr_;
public:
    AudioMixer(int sr=SAMPLE_RATE) : sr_(sr) {}
    void addTrack(const std::string& n, const AudioBuffer& b, float v=1.0f) {
        tracks_.emplace_back(n, b, v);
    }
    AudioBuffer mixDown() {
        size_t maxLen=0;
        for (auto& t:tracks_) maxLen=std::max(maxLen, t.buffer.size());
        AudioBuffer out(0.0, sr_); out.samples.resize(maxLen, 0.0f);
        for (auto& t:tracks_)
            for (size_t i=0; i<t.buffer.size(); i++) out[i]+=t.buffer[i]*t.volume;
        out.normalize(0.9f);
        return out;
    }
    void printInfo() const {
        std::cout << "  ┌─────────────────────────────────────┐" << std::endl;
        std::cout << "  │         오디오 믹서                  │" << std::endl;
        std::cout << "  ├─────────────────────────────────────┤" << std::endl;
        for (size_t i=0; i<tracks_.size(); i++) {
            std::cout << "  │ " << (i+1) << ". " << tracks_[i].name;
            for (int j=int(tracks_[i].name.size()); j<20; j++) std::cout<<' ';
            int bar=int(tracks_[i].volume*10);
            std::cout<<"["; for (int j=0;j<10;j++) std::cout<<(j<bar?'#':'.'); std::cout<<"]│\n";
        }
        std::cout << "  └─────────────────────────────────────┘" << std::endl;
    }
};

// ============================================================================
// 8단계: 비트 시퀀서 (패턴 기반 드럼 머신)
// ============================================================================
//  스텝: 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
//  킥:  [X][ ][ ][ ][X][ ][ ][ ][X][ ][ ][ ][X][ ][ ][ ]
//  스네: [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
//  햇:  [X][ ][X][ ][X][ ][X][ ][X][ ][X][ ][X][ ][X][ ]
class BeatSequencer {
public:
    static constexpr int STEPS = 16;
    struct Drum {
        std::string name; std::array<bool,STEPS> pat; float vol;
        Drum(const std::string& n, float v=0.8f) : name(n), vol(v) { pat.fill(false); }
    };
private:
    std::vector<Drum> drums_; double bpm_; int sr_;

    // 킥 드럼 - 쿵! (사인파 + 주파수하강)
    AudioBuffer genKick(double dur) {
        AudioBuffer b(dur,sr_);
        for (size_t i=0;i<b.size();i++) {
            double t=double(i)/sr_;
            double f=150*std::exp(-t*10)+50, a=std::exp(-t*8);
            b[i]=float(a*std::sin(TWO_PI*f*t));
        } return b;
    }
    // 스네어 - 착! (노이즈 + 톤)
    AudioBuffer genSnare(double dur) {
        AudioBuffer b(dur,sr_);
        std::random_device rd; std::mt19937 gen(rd());
        std::uniform_real_distribution<float> dist(-1,1);
        for (size_t i=0;i<b.size();i++) {
            double t=double(i)/sr_, a=std::exp(-t*12);
            b[i]=float(a*(0.4*std::sin(TWO_PI*200*t)+0.6*dist(gen)));
        } return b;
    }
    // 하이햇 - 치! (필터링된 노이즈)
    AudioBuffer genHiHat(double dur) {
        auto b=WaveGen::whiteNoise(dur,0.5,sr_);
        for (size_t i=0;i<b.size();i++) b[i]*=float(std::exp(-double(i)/sr_*30));
        return b;
    }
public:
    BeatSequencer(double bpm=120, int sr=SAMPLE_RATE) : bpm_(bpm), sr_(sr) {}
    void addDrum(const std::string& n, float v=0.8f) { drums_.emplace_back(n,v); }

    // "X...X...X...X..." 형태로 패턴 설정 (X=소리냄)
    void setPattern(int idx, const std::string& p) {
        if (idx<0||idx>=int(drums_.size())) return;
        for (int i=0;i<STEPS&&i<int(p.size());i++) drums_[idx].pat[i]=(p[i]=='X'||p[i]=='x');
    }
    void printPattern() const {
        std::cout<<"  비트 시퀀서 (BPM: "<<bpm_<<")"<<std::endl;
        std::cout<<"  스텝:   ";
        for (int i=0;i<STEPS;i++) std::cout<<(i+1<10?" ":"")<<(i+1)<<" ";
        std::cout<<std::endl<<"  "<<std::string(STEPS*3+10,'-')<<std::endl;
        for (auto& d:drums_) {
            std::cout<<"  "<<d.name;
            for (int i=int(d.name.size());i<8;i++) std::cout<<' ';
            for (int i=0;i<STEPS;i++) std::cout<<(d.pat[i]?"[X]":"[ ]");
            std::cout<<std::endl;
        }
        std::cout<<std::endl;
    }
    AudioBuffer render(int bars=1) {
        double stepDur = 60.0/bpm_/4.0;
        AudioBuffer out(stepDur*STEPS*bars, sr_);
        double soundDur = stepDur*2;
        for (int bar=0;bar<bars;bar++) {
            for (int step=0;step<STEPS;step++) {
                int off=int((bar*STEPS+step)*stepDur*sr_);
                for (size_t d=0;d<drums_.size();d++) {
                    if (!drums_[d].pat[step]) continue;
                    AudioBuffer snd(0.0,sr_);
                    if (drums_[d].name=="Kick") snd=genKick(soundDur);
                    else if (drums_[d].name=="Snare") snd=genSnare(soundDur);
                    else snd=genHiHat(soundDur);
                    for (size_t i=0;i<snd.size();i++) {
                        size_t oi=off+i;
                        if (oi<out.size()) out[oi]+=snd[i]*drums_[d].vol;
                    }
                }
            }
        }
        return out;
    }
};

// ============================================================================
// 데모 함수들
// ============================================================================

void demoWaveforms() {
    std::cout << "=== 데모 1: 기본 파형 ===" << std::endl;
    struct { std::string name; AudioBuffer(*fn)(double,double,double,int); } waves[] = {
        {"사인파 (Sine)", WaveGen::sine},
        {"사각파 (Square)", WaveGen::square},
        {"톱니파 (Sawtooth)", WaveGen::sawtooth},
        {"삼각파 (Triangle)", WaveGen::triangle},
    };
    for (auto& w : waves) {
        std::cout << "  " << w.name << " - 440Hz" << std::endl;
        auto buf = w.fn(440.0, 1.0, 1.0, SAMPLE_RATE);
        buf.printWaveform(50, 5);
        std::cout << std::endl;
    }
    std::cout << "  백색 소음 (White Noise)" << std::endl;
    auto noise = WaveGen::whiteNoise(1.0, 0.5);
    noise.printWaveform(50, 5);
    std::cout << std::endl;
}

void demoEffects() {
    std::cout << "=== 데모 2: 오디오 이펙트 ===" << std::endl;
    auto orig = WaveGen::sine(440.0, 0.5);
    // 페이드
    std::cout << "  [1] 페이드 인/아웃" << std::endl;
    auto faded = WaveGen::sine(440.0, 1.0);
    Effects::fadeIn(faded, 0.3); Effects::fadeOut(faded, 0.3);
    faded.printWaveform(50, 5); std::cout<<std::endl;
    // 에코
    std::cout << "  [2] 에코" << std::endl;
    auto echoed = Effects::echo(orig, 0.15, 0.4, 3);
    echoed.printWaveform(50, 5); std::cout<<std::endl;
    // 디스토션
    std::cout << "  [3] 디스토션" << std::endl;
    auto dist = WaveGen::sine(440.0, 0.5);
    Effects::distortion(dist, 3.0f, 0.5f);
    dist.printWaveform(50, 5); std::cout<<std::endl;
    // 필터
    std::cout << "  [4] 로우패스 필터" << std::endl;
    auto filt = WaveGen::square(440.0, 0.5);
    Effects::lowPassFilter(filt, 0.05f);
    filt.printWaveform(50, 5); std::cout<<std::endl;
}

void demoADSR() {
    std::cout << "=== 데모 3: ADSR 엔벨로프 ===" << std::endl;
    ADSREnvelope env(0.05, 0.1, 0.6, 0.3);
    auto note = WaveGen::sine(440.0, 0.8);
    std::cout << "  적용 전:" << std::endl;
    note.printWaveform(50, 5);
    env.apply(note, 0.5);
    std::cout << "  적용 후 (A=0.05 D=0.1 S=0.6 R=0.3):" << std::endl;
    note.printWaveform(50, 5);
    std::cout << std::endl;
}

void demoMelody() {
    std::cout << "=== 데모 4: 도레미파솔라시도 멜로디 ===" << std::endl;
    Synthesizer synth(WaveType::TRIANGLE, 0.7);
    synth.setEnvelope(0.01, 0.05, 0.6, 0.1);
    int melody[] = {Notes::C4, Notes::D4, Notes::E4, Notes::F4,
                    Notes::G4, Notes::A4, Notes::B4, Notes::C5};
    const char* names[] = {"도","레","미","파","솔","라","시","도'"};
    double noteDur=0.3;
    AudioBuffer out(noteDur*8+0.5, SAMPLE_RATE);
    std::cout << "  멜로디: ";
    for (int i=0; i<8; i++) {
        std::cout<<names[i]<<"("<<int(Notes::freq(melody[i]))<<"Hz) ";
        auto nb=synth.playNote(melody[i], noteDur);
        int off=int(i*noteDur*SAMPLE_RATE);
        for (size_t j=0;j<nb.size();j++) { size_t idx=off+j; if(idx<out.size()) out[idx]+=nb[j]; }
    }
    std::cout<<std::endl;
    out.normalize(0.8f);
    out.printWaveform(60, 7);
    if (WavWriter::save("melody_doremi.wav", out))
        std::cout<<"  WAV 저장: melody_doremi.wav (재생하면 도레미가 들립니다!)"<<std::endl;
    std::cout<<std::endl;
}

void demoMixer() {
    std::cout << "=== 데모 5: 오디오 믹서 ===" << std::endl;
    AudioMixer mixer;
    // 베이스 트랙
    auto bass = WaveGen::sine(110.0, 2.0, 0.6);
    Effects::fadeIn(bass,0.1); Effects::fadeOut(bass,0.3);
    mixer.addTrack("Bass (110Hz)", bass, 0.7f);
    // 멜로디 트랙
    Synthesizer ms(WaveType::TRIANGLE, 0.5); ms.setEnvelope(0.02,0.05,0.5,0.1);
    AudioBuffer mel(2.0, SAMPLE_RATE);
    int chordNotes[] = {Notes::C4, Notes::E4, Notes::G4, Notes::C5};
    for (int i=0;i<4;i++) {
        auto n=ms.playNote(chordNotes[i],0.4);
        int off=int(i*0.5*SAMPLE_RATE);
        for (size_t j=0;j<n.size();j++) { size_t idx=off+j; if(idx<mel.size()) mel[idx]+=n[j]; }
    }
    mixer.addTrack("Melody", mel, 0.8f);
    // 하이햇 리듬
    auto hh=WaveGen::whiteNoise(2.0, 0.2);
    double eighth=60.0/120.0/2.0;
    for (size_t i=0;i<hh.size();i++) {
        double t=double(i)/SAMPLE_RATE, beat=std::fmod(t,eighth);
        hh[i] = beat>0.05 ? 0.0f : hh[i]*float(std::exp(-beat*100));
    }
    mixer.addTrack("HiHat", hh, 0.4f);
    mixer.printInfo();
    auto mixed=mixer.mixDown();
    mixed.printWaveform(60, 7);
    if (WavWriter::save("mixer_output.wav", mixed))
        std::cout<<"  WAV 저장: mixer_output.wav"<<std::endl;
    std::cout<<std::endl;
}

void demoBeat() {
    std::cout << "=== 데모 6: 비트 시퀀서 (드럼 머신) ===" << std::endl;
    BeatSequencer seq(120.0);
    seq.addDrum("Kick", 0.9f);
    seq.addDrum("Snare", 0.7f);
    seq.addDrum("HiHat", 0.5f);
    // 기본 록 비트 패턴
    seq.setPattern(0, "X...X...X...X...");
    seq.setPattern(1, "....X.......X...");
    seq.setPattern(2, "X.X.X.X.X.X.X.X.");
    seq.printPattern();
    auto drum=seq.render(2); drum.normalize(0.8f);
    drum.printWaveform(60, 7);
    if (WavWriter::save("drum_beat.wav", drum))
        std::cout<<"  WAV 저장: drum_beat.wav (쿵착쿵착 드럼비트!)"<<std::endl;
    std::cout<<std::endl;
}

void demoFullSong() {
    std::cout << "=== 데모 7: 종합 - 미니 음악 ===" << std::endl;
    double bpm=120, beat=60.0/bpm, bar=beat*4, songDur=bar*4;
    AudioMixer mixer;
    // 베이스
    std::cout<<"  [1] 베이스..."<<std::endl;
    Synthesizer bs(WaveType::SAWTOOTH,0.4); bs.setEnvelope(0.01,0.1,0.5,0.1);
    AudioBuffer bassL(songDur,SAMPLE_RATE);
    int bassN[]={36,36,41,43};
    for (int i=0;i<4;i++) {
        auto n=bs.playNote(bassN[i],bar*0.8);
        int off=int(i*bar*SAMPLE_RATE);
        for (size_t j=0;j<n.size();j++){size_t idx=off+j;if(idx<bassL.size())bassL[idx]+=n[j];}
    }
    Effects::lowPassFilter(bassL,0.15f);
    mixer.addTrack("Bass",bassL,0.6f);
    // 코드
    std::cout<<"  [2] 코드..."<<std::endl;
    Synthesizer cs(WaveType::TRIANGLE,0.25); cs.setEnvelope(0.05,0.2,0.4,0.3);
    AudioBuffer chT(songDur,SAMPLE_RATE);
    int chords[][3]={{Notes::C4,Notes::E4,Notes::G4},{Notes::C4,Notes::E4,Notes::G4},
                     {Notes::F4,Notes::A4,Notes::C5},{Notes::G4,Notes::B4,74}};
    for (int b=0;b<4;b++) for (int c=0;c<3;c++) {
        auto n=cs.playNote(chords[b][c],bar*0.9);
        int off=int(b*bar*SAMPLE_RATE);
        for (size_t j=0;j<n.size();j++){size_t idx=off+j;if(idx<chT.size())chT[idx]+=n[j];}
    }
    mixer.addTrack("Chords",chT,0.5f);
    // 드럼
    std::cout<<"  [3] 드럼..."<<std::endl;
    BeatSequencer dr(bpm); dr.addDrum("Kick",0.9f); dr.addDrum("Snare",0.6f); dr.addDrum("HiHat",0.4f);
    dr.setPattern(0,"X...X...X...X..."); dr.setPattern(1,"....X.......X..."); dr.setPattern(2,"X.X.X.X.X.X.X.X.");
    mixer.addTrack("Drums",dr.render(4),0.7f);
    // 믹스
    std::cout<<"  [4] 믹싱..."<<std::endl;
    mixer.printInfo();
    auto final_=mixer.mixDown();
    Effects::fadeIn(final_,0.5); Effects::fadeOut(final_,1.0);
    final_.printWaveform(60, 9);
    std::cout<<"  길이: "<<final_.duration()<<"초, 샘플: "<<final_.size()<<std::endl;
    if (WavWriter::save("mini_song.wav", final_))
        std::cout<<"  WAV 저장: mini_song.wav (실제 재생 가능!)"<<std::endl;
    std::cout<<std::endl;
}

// ============================================================================
// 메인 함수
// ============================================================================
/*
=============================================================================
  실행 흐름 가이드 (작업 디렉토리에 .wav 파일 생성됨)
=============================================================================
  demoWaveforms: sine.wav, square.wav, saw.wav, triangle.wav (각 1초)
    sine: 부드러운 sinusoid
    square: 사각파 (종 모양 스펙트럼, 거친 소리)
    saw: 톱니파
    triangle: 삼각파

  demoEffects: dry.wav vs delay.wav vs reverb.wav vs lowpass.wav
    각각 동일 입력에 effect 적용 결과

  demoADSR: piano_note.wav (피아노 형 envelope)
    Attack 50ms → Decay 100ms → Sustain 0.7 → Release 200ms

  demoMelody: melody.wav (간단한 곡, C-D-E-F-G ...)

  demoMixer: 여러 트랙 (드럼+베이스+멜로디) 합성 → mix.wav

  demoBeat: drumbeat.wav (kick + snare + hihat 패턴)

  demoFullSong: full_song.wav (~10초 곡, 모든 요소 통합)

  파일 크기:
    44.1kHz / 16bit mono = 88.2 KB/sec
    1초 → ~88KB, 10초 → ~880KB
  헤더는 RIFF/WAVE 44바이트
=============================================================================
*/

int main() {
    std::cout << "============================================================" << std::endl;
    std::cout << "  오디오 프로세싱 엔진 (Audio Processing Engine)" << std::endl;
    std::cout << "  실시간 오디오에서 GC → 끊김 → C++ 필수!" << std::endl;
    std::cout << "  WAV 파일 생성 → 미디어 플레이어로 재생 가능" << std::endl;
    std::cout << "============================================================" << std::endl << std::endl;

    demoWaveforms();
    demoEffects();
    demoADSR();
    demoMelody();
    demoMixer();
    demoBeat();
    demoFullSong();

    std::cout << "============================================================" << std::endl;
    std::cout << "  완료! 생성된 WAV 파일을 재생해 보세요." << std::endl;
    std::cout << "============================================================" << std::endl;
    return 0;
}
