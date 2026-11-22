# pyquant-pricer

Python으로 직접 구현하는 금융상품 프라이싱 및 리스크 라이브러리입니다.
날짜 관례, 시장 데이터, 상품 평가, 리스크 측정까지 단계적으로 구현하며 금융공학을 공부한 기록입니다.

## 구조

| 모듈 | 역할 | 상태 |
|---|---|---|
| `Utility` | 날짜·영업일 처리, Day Count Convention, 쿠폰 스케줄, 정규분포 함수, 난수 생성, 숄레츠키 분해 | 진행 중 |
| `Core` | 상품과 무관한 수치 엔진 (이항트리, 단일/다자산 몬테카를로 경로 생성) | 진행 중 |
| `Product` | 개별 상품 평가 (주식 옵션, FX 옵션, 디지털 옵션) | 진행 중 |
| `DB` | 시장 데이터 DB 연결 (MySQL) | 착수 |
| `Market` | 금리 커브, 변동성 등 시장 데이터 | 예정 |
| `Risk` | 민감도(Greeks, Duration), VaR | 예정 |

```
pyquant-pricer/
├── Utility/
│   ├── Date.py         # 날짜 변환, 휴일/영업일, Day Count, 쿠폰 스케줄
│   └── Math.py         # 정규분포, 유사난수(LCG), Box-Muller, 숄레츠키 분해
├── Core/
│   ├── Tree.py         # CRR 이항트리 엔진 (payoff 함수를 받아 후진귀납)
│   └── MC.py           # GBM 몬테카를로 경로 생성 (단일/다자산, FX)
├── Product/
│   ├── BSOption.py     # Black-Scholes 해석해 (바닐라, 디지털)
│   ├── CRROption.py    # 이항트리 바닐라 옵션 (아메리칸/유러피안)
│   └── FXOption.py     # Garman-Kohlhagen FX 옵션
├── DB/
│   └── DBConn.py       # DB 연결 (작업 중)
└── main.py             # 실행/테스트용 스크립트
```

의존 방향은 `Utility ← Core ← Product` 한 방향입니다.

- **Core**는 *어떻게 계산하는가*(수치 방법)만 담당하고, 행사가·콜/풋 같은 계약 조건은 모릅니다.
- **Product**는 *무엇을 계산하는가*(payoff, 행사 규칙)를 정의하고, payoff를 **함수 객체**로 Core 엔진에 넘깁니다.
- 덕분에 같은 엔진으로 유러피안·아메리칸을 모두 계산하고, 새 상품은 payoff만 추가하면 됩니다.
- `Product`는 **계산 방법별 모듈**로 나뉘고, 모듈마다 같은 이름의 함수(`VanillaPayoff` 등)를 둡니다. 모듈 이름으로 구분해서 호출합니다. (예: `BSOption.VanillaPayoff`, `CRROption.VanillaPayoff`)

## 구현된 기능

### `Utility/Date.py`

| 함수 | 설명 |
|---|---|
| `ConvDate(d)` | `20240115`, `"20240115"`, `"2024-01-15"`, `date`, `datetime`을 `datetime.date`로 변환 |
| `IsHoliday(d, exchange="XKRX")` | 주말 또는 거래소 휴일 여부 |
| `AdjustHoliday(d, exchange="XKRX", convention="MF")` | 휴일 조정 (Business Day Convention) |
| `AddBizDay(d, offset, exchange="XKRX", convention="MF")` | 영업일 기준 ±N일 이동 (`offset=0`이면 휴일 조정만 수행) |
| `Time2Mat(start, end, conv="ACT/ACT")` | 두 날짜 사이의 연 단위 기간 |
| `MakeSchedule(start, end, yearlyCpnNums, stub="L", exchange="XKRX", convention="MF")` | 쿠폰 스케줄 생성 |

- **거래소 휴일**: [`holidays`](https://pypi.org/project/holidays/) 패키지의 `financial_holidays`를 사용하며, 연도별 결과를 `lru_cache`로 캐싱합니다.
  - 지원 코드 예시: `XKRX`(한국), `XNYS`(뉴욕), `XSHG`(상하이), `XHKG`(홍콩), `XJPX`(일본), `XLON`(런던), `XETR`(프랑크푸르트)
- **Business Day Convention**
  - `"F"`: Following — 다음 영업일
  - `"MF"`: Modified Following — 다음 영업일이 다음 달로 넘어가면 이전 영업일
  - `"P"`: Preceding — 이전 영업일
- **Day Count Convention** (`Time2Mat`)
  - `"ACT/365"`: ACT/365 Fixed
  - `"ACT/360"`: ACT/360
  - `"ACT/ACT"`: ACT/ACT (ISDA) — 연도별 실제 일수(윤년 포함)로 나눠 합산
- **쿠폰 스케줄** (`MakeSchedule`)
  - 만기일에서 역산하여 생성하므로 월말 날짜가 밀리지 않음 (1/31 → 2/29 → 3/31)
  - 연 지급 횟수 1, 2, 4, 6, 12회 지원
  - Stub 처리: `"S"`(Short front stub), `"L"`(Long front stub)
  - 반환값: `(계산일 리스트, 지급일 리스트)` — 쿠폰 계산일(달력일)과 휴일 조정된 지급일(영업일)을 분리해서 반환. 시작일은 조정하지 않습니다.

### `Utility/Math.py`

| 함수 | 설명 |
|---|---|
| `PDF(x)` | 표준정규분포 확률밀도함수 |
| `CND(x)` | 표준정규분포 누적분포함수 (Abramowitz & Stegun 근사) |
| `SetSeed(seed=None)` | 난수 시드 설정 (`None`이면 현재 시각, 정수면 재현 가능한 난수열) |
| `GenRnd()` | 선형합동생성기(LCG)로 `(0, 1)` 균등난수 2개 생성 |
| `BoxMullerRnd(shape=1)` | Box-Muller 변환으로 원하는 shape의 표준정규난수 배열 생성 (`int` 또는 `tuple`) |
| `Cholesky(corr)` | 상관행렬을 하삼각행렬 $L$로 분해 ($\rho = LL^T$), 직접 구현 |

- `CND`: Abramowitz & Stegun (1964) 다항 근사, 오차 약 $10^{-7}$ 수준

$$N(x) \approx 1 - \phi(x)\,(a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5), \quad t = \frac{1}{1 + p\,|x|}$$

- `GenRnd`: ANSI C(Watcom) 파라미터 $X_{n+1} = (aX_n + c) \bmod m$, $a = 1103515245,\ c = 12345,\ m = 2^{31}$. 생성기 상태는 모듈 안에 유지되어 호출마다 이어지며, 초기 시드는 import 시점의 시각(μs)입니다. `SetSeed(42)`처럼 고정하면 같은 결과를 재현할 수 있습니다.
- `BoxMullerRnd`: 균등난수 $U_1, U_2$로부터

$$Z_1 = \sqrt{-2\ln U_1}\cos(2\pi U_2), \quad Z_2 = \sqrt{-2\ln U_1}\sin(2\pi U_2)$$

- `Cholesky`: $\rho_{ij}$는 $L$의 i행과 j행의 내적이라는 점을 이용해, 위에서 아래로·왼쪽에서 오른쪽으로 한 원소씩 구합니다. 대각선에서 제곱근 안이 0 이하이면 양의 정부호가 아니므로 `ValueError`를 냅니다.
  - 3×3 손 계산 과정: [`Utility/숄레츠키분해_수기계산.jpg`](Utility/숄레츠키분해_수기계산.jpg)

### `Core/Tree.py`

| 함수 | 설명 |
|---|---|
| `CRRTree(S, T, R, sigma, FuncPayoff, Q=0.0, N=252, earlyExercise=False)` | Cox-Ross-Rubinstein (1979) 이항트리 |

- `FuncPayoff`: 주가(스칼라 또는 배열)를 받아 payoff를 돌려주는 **함수**. 호출 결과가 아니라 함수 자체를 넘깁니다.
- `earlyExercise=True`면 각 노드에서 `max(계속보유가치, 행사가치)`(아메리칸), `False`면 할인 기대값만 사용(유러피안)합니다.
- `N`은 **연간** 스텝 수이며, 총 스텝 수는 `round(N × T)`입니다. `T == 0`이면 `FuncPayoff(S)`를 반환합니다.

$$u = e^{\sigma\sqrt{\Delta t}}, \quad d = 1/u, \quad p = \frac{e^{(R-Q)\Delta t} - d}{u - d}, \quad V_i = e^{-R\Delta t}\left[p\,V_{i+1}^{up} + (1-p)\,V_{i+1}^{down}\right]$$

### `Core/MC.py`

| 함수 | 설명 |
|---|---|
| `EQMonteCarlo(S, T, R, sigma, corr=None, Q=None, N=252, numsSim=10_000)` | 단일/다자산 범용 GBM 경로 시뮬레이션 (상관계수 반영) |
| `FXMonteCarlo(S, T, R_d, R_f, sigma, N=252, numsSim=10_000)` | Garman-Kohlhagen 환율 경로 (`EQMonteCarlo`에 `R=R_d`, `Q=R_f`로 위임) |
| `EQSingleMonteCarlo(S, T, R, sigma, Q=0.0, N=252, numsSim=10_000)` | 단일 자산 전용 (테스트·비교용, 2차원 반환) |

**입력**

| 파라미터 | 형태 | 비고 |
|---|---|---|
| `S`, `sigma`, `Q` | 스칼라 또는 길이 n 배열 | 자산마다 다른 값. 스칼라는 길이 1 배열로 처리 |
| `corr` | n×n 상관행렬 | 다자산이면 필수, 단일 자산이면 생략 시 `[[1.0]]` |
| `R`, `T`, `N`, `numsSim` | 스칼라 | 모든 자산이 같은 할인율·시간축을 공유 |

**계산 과정**

1. 독립 표준정규난수 `Z`를 shape `(numsSim/2, step, n)`으로 생성 (`BoxMullerRnd`)
2. **Antithetic Variates**: $Z$와 $-Z$를 이어 붙여 분산 감소
3. **상관 부여**: `Z @ L.T` — 같은 시점의 자산끼리만 섞이고, 시점 간 독립성은 유지
4. 자산별 drift·변동성을 브로드캐스팅으로 적용하고 시간 축(`axis=1`)으로 누적

$$S^{(i)}_{t+\Delta t} = S^{(i)}_t \exp\left[\left(R - Q_i - \tfrac{1}{2}\sigma_i^2\right)\Delta t + \sigma_i\sqrt{\Delta t}\,W^{(i)}\right], \qquad W = LZ$$

- 반환값: shape `(numsSim, step + 1, n)`의 경로 배열 (첫 시점은 `S`), `step = round(T × N)`. **단일 자산도 3차원**입니다.
- 입력 검사: `S`, `sigma` ≤ 0 또는 `T` < 0, 배열 길이 불일치, `corr` 크기 불일치, 양의 정부호가 아닌 상관행렬이면 `ValueError`
- `numsSim`이 홀수면 antithetic 쌍 구조 때문에 경로가 `numsSim − 1`개 생성됩니다.
- 같은 시드에서 `EQMonteCarlo(..., n=1)`과 `EQSingleMonteCarlo`의 경로는 정확히 일치합니다.
- FX의 `S`는 **외국 통화 1단위당 국내 통화 가격**입니다. (USD/KRW = 1,400이면 `R_d`=원화 금리, `R_f`=달러 금리)

### `Product/BSOption.py`

| 함수 | 설명 |
|---|---|
| `VanillaPayoff(S, K, T, R, sigma, Q=0.0, isCall=True)` | Black-Scholes(-Merton) 유러피안 옵션, 연속 배당수익률 `Q` 반영 |
| `DigitalPayoff(S, K, T, R, sigma, cpn1, cpn2, Q=0.0)` | 디지털 옵션: 만기 주가가 `K` 초과면 `cpn2`, 이하면 `cpn1` 지급 |

- 콜/풋은 `cpFlag`(콜 `+1`, 풋 `−1`)로 하나의 식에 통합했습니다.
- `T == 0`이면 내재가치(만기 지급액)를 반환합니다.

$$d_1 = \frac{\ln(S/K) + (R - Q + \tfrac{1}{2}\sigma^2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

$$V_{vanilla} = \text{cpFlag}\cdot\left[S e^{-QT} N(\text{cpFlag}\cdot d_1) - K e^{-RT} N(\text{cpFlag}\cdot d_2)\right]$$

$$V_{digital} = e^{-RT}\left[\text{cpn2}\cdot N(d_2) + \text{cpn1}\cdot N(-d_2)\right]$$

### `Product/CRROption.py`

| 함수 | 설명 |
|---|---|
| `VanillaPayoff(S, K, T, R, sigma, Q=0.0, isCall=True, N=252, isAmerican=True)` | `Core.Tree.CRRTree`로 계산하는 바닐라 옵션 (아메리칸/유러피안 선택) |

- 함수 안에서 `K`와 `cpFlag`를 기억하는 payoff 함수(클로저)를 만들어 `CRRTree`에 넘깁니다.
- `isAmerican=False`는 스텝 수를 늘릴수록 `BSOption.VanillaPayoff`로 수렴하므로, 두 방법을 서로 검증하는 데 쓸 수 있습니다.

### `Product/FXOption.py`

| 함수 | 설명 |
|---|---|
| `VanillaPayoff(S, K, T, R_d, R_f, sigma, isCall=True)` | Garman-Kohlhagen (1983) FX 유러피안 옵션 |

- Black-Scholes에서 배당수익률 `Q` 자리에 외국 금리 `R_f`, 무위험금리 자리에 국내 금리 `R_d`가 들어간 형태입니다.

$$V = \text{cpFlag}\cdot\left[S e^{-R_f T} N(\text{cpFlag}\cdot d_1) - K e^{-R_d T} N(\text{cpFlag}\cdot d_2)\right], \quad d_1 = \frac{\ln(S/K) + (R_d - R_f + \tfrac{1}{2}\sigma^2)T}{\sigma\sqrt{T}}$$

## 사용 예시

```python
from Utility.Date import MakeSchedule, Time2Mat, AdjustHoliday, AddBizDay
from Utility.Math import CND

# 3년 만기, 분기 지급, 시작일이 쿠폰일과 어긋나는 경우 (Short front stub)
calcDates, payDates = MakeSchedule(20240301, 20270115, 4, stub="S")
calcDates[:3]
# [date(2024, 3, 1), date(2024, 4, 15), date(2024, 7, 15)]

# ACT/ACT ISDA: 184/366 + 181/365
Time2Mat("2024-07-01", 20250701, conv="ACT/ACT")
# 0.99862...

# 2026-01-31(토) → Modified Following → 2026-01-30(금)
AdjustHoliday(20260131, exchange="XKRX", convention="MF")
# date(2026, 1, 30)

# 2026-01-30(금) + 1 영업일
AddBizDay(20260130, 1)
# date(2026, 2, 2)

CND(1.96)
# 0.97500...
```

```python
from Product import BSOption, CRROption, FXOption

# Black-Scholes
BSOption.VanillaPayoff(100, 100, 1.0, 0.03, 0.2)                 # 9.4134 (Call)
BSOption.VanillaPayoff(100, 100, 1.0, 0.03, 0.2, isCall=False)   # 6.4579 (Put)
BSOption.DigitalPayoff(100, 100, 1.0, 0.03, 0.2, 0, 10)          # 5.0457 (K 초과 시 10 지급)

# 이항트리
CRROption.VanillaPayoff(100, 100, 1.0, 0.03, 0.2, isCall=False)                    # 6.7392 (아메리칸 풋)
CRROption.VanillaPayoff(100, 100, 1.0, 0.03, 0.2, isCall=False, isAmerican=False)  # 6.4501 (유러피안 풋)
CRROption.VanillaPayoff(100, 100, 1.0, 0.03, 0.2, isCall=False, N=2000, isAmerican=False)  # 6.4570 → BS로 수렴

# FX (USD/KRW 1,400, 원화 3%, 달러 4.5%, 변동성 10%)
FXOption.VanillaPayoff(1400, 1400, 1.0, 0.03, 0.045, 0.1)                # 44.26 (Call)
FXOption.VanillaPayoff(1400, 1400, 1.0, 0.03, 0.045, 0.1, isCall=False)  # 64.49 (Put)
```

```python
from Utility.Math import SetSeed, Cholesky
from Core.MC import EQMonteCarlo

corr = [[1.0, 0.5, 0.3],
        [0.5, 1.0, 0.4],
        [0.3, 0.4, 1.0]]

Cholesky(corr)
# [[1.0,    0.0,    0.0   ],
#  [0.5,    0.8660, 0.0   ],
#  [0.3,    0.2887, 0.9092]]

# 3자산 상관 경로 (시드 고정으로 재현 가능)
SetSeed(42)
paths = EQMonteCarlo(S=[100, 50, 200], T=1.0, R=0.03, sigma=[0.2, 0.3, 0.25],
                     corr=corr, Q=[0.01, 0.0, 0.02])
paths.shape
# (10000, 253, 3)  ← (경로, 시점, 자산)
# 로그수익률 상관계수 ≈ 0.499 / 0.299 / 0.398

# 단일 자산은 corr 생략 가능
EQMonteCarlo(100, 1.0, 0.03, 0.2, Q=0.01).shape
# (10000, 253, 1)
```

```python
from Core.Tree import CRRTree

# Core 엔진을 직접 사용: payoff 함수만 바꾸면 새로운 상품을 계산할 수 있음
digitalCall = lambda s: (s > 100) * 10.0   # 만기 주가가 100 초과면 10 지급
CRRTree(100, 1.0, 0.03, 0.2, digitalCall)
# 4.8022 (해석해 5.0457 — payoff가 불연속이라 트리 오차가 큰 편)
```

## 설치

```bash
pip install -r requirements.txt
```

- 의존성: `holidays`, `python-dateutil`, `numpy`
- 모든 import는 저장소 루트 기준입니다. 모듈 파일을 직접 실행할 때는 루트에서 `-m` 옵션을 사용하세요.
  ```bash
  python -m Core.MC        # O
  python Core/MC.py        # X: ModuleNotFoundError: No module named 'Utility'
  ```
- Python 3.13에서 테스트했습니다.

## TODO

- `Time2Mat`: 30/360 (2006 ISDA Definitions 4.16(f)) 지원
- 경로에 payoff 함수를 적용해 할인 평균을 내는 범용 몬테카를로 프라이서 (`Core`)
- 상품별 `Product` 구성: 스텝다운 ELS(낙인, 스노우볼 등 변형 포함)
- `BoxMullerRnd` 속도 개선 (현재 Python 반복문 기반)
- `DB` 시장 데이터 연결, `Market` / `Risk` 모듈 구현

## License

[LICENSE](LICENSE) 참고
