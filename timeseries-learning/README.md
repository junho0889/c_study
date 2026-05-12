# 시계열 분석 & AI 적용 학습 가이드

통계 기반 시계열 분석부터 최신 딥러닝/Foundation 모델, 그리고 산업현장 응용까지
**17단계**로 배우는 시계열 AI 종합 교재입니다.
모든 코드에 한글 주석, 비유, ASCII 그림, 실전 예제, 연습문제가 포함되어 있습니다.

> 본 가이드는 `numpy-learning`, `pandas-learning`, `python-ml-learning`, `deep-learning-learning`,
> `pytorch-learning`, `tensorflow-learning` 과 함께 학습하면 시너지가 큽니다.
> 시계열은 “시간”이라는 축이 하나 더 붙은 ML이므로, 일반 ML 지식 위에 시간 처리 노하우를 쌓는 구조로 설계했습니다.

## 학습 로드맵 한 줄 요약

```
   통계 기초 ──▶ ARIMA ──▶ 지수평활 ──▶ ML 예측 ──▶ DL 예측 ──▶ Foundation 모델
                                              │
                                              ▼
                                     이상탐지 · 추천 · 실시간 · 실전 프로젝트
```

## 커리큘럼

### PART 1 — 시계열 기초 (01~03)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 01 | 시계열 기초 | 시계열이란?, 정상성(stationarity), 자기상관(ACF/PACF), 시각화 |
| 02 | 시계열 분해 | 트렌드 / 계절성 / 잔차, 가법·승법 분해, STL 분해 |
| 03 | 차분과 변환 | 차분, 로그 변환, Box-Cox, 단위근 검정(ADF/KPSS), white noise |

### PART 2 — 전통 통계 모델 (04~06)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 04 | ARIMA/SARIMA | AR, MA, ARMA → ARIMA → SARIMA, 차수 식별, 잔차 진단 |
| 05 | 지수평활 | SES, Holt, Holt-Winters, ETS 분류 체계 |
| 06 | 다변량 시계열 | VAR, VECM, 그렌저 인과성, 공적분 |

### PART 3 — 머신러닝 기반 예측 (07~09)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 07 | 피처 엔지니어링 | lag / rolling / EWM / calendar / Fourier 피처, 타깃 인코딩 |
| 08 | ML 예측 모델 | RandomForest, XGBoost, LightGBM, CatBoost 시계열 적용 |
| 09 | 평가와 검증 | MAE/RMSE/MAPE/SMAPE/MASE, walk-forward CV, 백테스팅 |

### PART 4 — 딥러닝 기반 예측 (10~13)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 10 | RNN / LSTM / GRU | 시퀀스 모델링, 셀 구조, vanishing gradient, 양방향 |
| 11 | 1D CNN & TCN | dilated conv, causal padding, receptive field 계산 |
| 12 | Transformer 계열 | Informer, Autoformer, PatchTST, iTransformer, 어텐션 핵심 |
| 13 | N-BEATS / N-HiTS | 잔차 스택 구조, basis function, 해석 가능 분해 |

### PART 5 — Foundation 모델과 LLM 적용 (14)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 14 | 시계열 Foundation 모델 | TimesFM, Chronos, Lag-Llama, Moirai, zero-shot 예측, LLM과의 결합 |

### PART 6 — 산업 응용 (15~17)
| 단계 | 주제 | 핵심 내용 |
|------|------|-----------|
| 15 | 이상 탐지 | 통계식(z-score/IQR), Isolation Forest, AE/VAE, GAN-AD, drift |
| 16 | 추천 & 수요예측 | 시퀀스 추천(SASRec), 수요예측, 재고/에너지/물류 적용 |
| 17 | 실전 프로젝트 | 다변량 센서 → ETL → 예측 + 이상탐지 + 알림까지 통합 파이프라인 |

## 학습 방법

1. **순서대로 학습** — 각 단계는 이전 단계의 개념을 전제로 합니다.
2. **챕터 끝의 연습문제** 를 직접 풀어보세요. 답안은 다음 챕터 앞부분에서 확인합니다.
3. **현장 데이터로 실험** — IoT 센서 로그, 매출 데이터, 트래픽 로그 등 본인이 가진 실데이터에 즉시 적용하세요.
4. **시각화 우선** — 시계열은 그림을 그려보는 것이 모든 분석의 시작입니다.

## 의존 라이브러리

```
numpy            # 배열 연산
pandas           # 시계열 자료구조 (DatetimeIndex, resample, rolling)
statsmodels      # ARIMA, ETS, ADF, VAR
scikit-learn     # ML 모델, 평가지표
xgboost / lightgbm # 그래디언트 부스팅
torch            # 딥러닝 (LSTM/Transformer/N-BEATS)
matplotlib       # 시각화
# 선택
darts, sktime, neuralforecast, mlforecast, prophet, ruptures
```

## “시계열 분석”과 “시계열 예측”의 차이

| 구분 | 분석(Analysis) | 예측(Forecasting) |
|------|----------------|-------------------|
| 목적 | 과거 데이터 안의 패턴/구조 이해 | 미래 값을 추정 |
| 산출물 | 트렌드, 계절성, 변화점, 관계식 | 점추정 + 예측구간 |
| 대표 도구 | STL, ADF, 인과성 검정 | ARIMA, LSTM, N-BEATS |
| 공통점 | 정상성·자기상관 같은 시계열 본질 개념을 똑같이 다룬다 |

본 가이드는 두 영역 모두 다룹니다 — 분석으로 데이터를 “이해”한 다음, 예측으로 미래를 “생성”합니다.
