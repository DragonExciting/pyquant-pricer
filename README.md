# pyquant-pricer

Python으로 직접 구현하는 금융상품 프라이싱 및 리스크 라이브러리입니다.
날짜 관례, 수치 엔진, 상품 평가, 시장 데이터까지 단계적으로 구현하며 금융공학을 공부한 기록입니다.

## 구조

| 모듈 | 역할 | 상태 |
|---|---|---|
| `Utility` | 날짜·영업일, Day Count, 쿠폰 스케줄, 정규분포, 난수 생성, 숄레츠키 분해, 해찾기(Newton·이분법) | 진행 중 |
| `Core` | 상품과 무관한 수치 엔진 (CRR 이항트리, 몬테카를로 경로 생성, BDT·FDM 예정) | 진행 중 |
| `Product` | 개별 상품 평가 (유러피안·아메리칸·디지털 옵션, 주식 선도, 채권 예정) | 진행 중 |
| `Market` | 할인 커브, 내재변동성, 그릭스 | 진행 중 |
| `DB` | 시장 데이터 DB 연결 (MySQL) | 진행 중 |

```
pyquant-pricer/
├── Utility/
│   ├── Date.py         # 날짜 변환, 휴일/영업일, Day Count, 쿠폰 스케줄
│   ├── Math.py         # 정규분포, 유사난수(LCG), Box-Muller, Marsaglia, 숄레츠키 분해
│   └── Solver.py       # 해찾기: Newton-Raphson(중앙차분), 이분법
├── Core/
│   ├── Tree.py         # CRR 이항트리 엔진 (payoff 함수를 받아 후진귀납), BDT 자리
│   ├── MC.py           # GBM 몬테카를로 경로 생성 (단일/다자산, FX)
│   └── FDM.py          # 유한차분법(Crank-Nicolson) 자리
├── Product/
│   ├── EurOpt.py       # Black-Scholes / Garman-Kohlhagen 닫힌 해 (바닐라, 디지털)
│   ├── AmeOpt.py       # 이항트리 바닐라 옵션 (아메리칸/유러피안)
│   ├── Fwd.py          # 주식 선도가격
│   └── Bnd.py          # 고정금리채 자리
├── Market/
│   ├── Curve.py        # 커브에서 할인계수 호출 (zero rate 선형보간)
│   ├── Vol.py          # 내재변동성 (Newton → 이분법), 역사적 변동성 자리
│   └── Greeks.py       # Black-Scholes 닫힌 해 Delta, Gamma, Vega
├── DB/
│   └── DBConn.py       # MySQL 연결 → pandas DataFrame
└── main.py             # 실행/테스트용 스크립트
```

의존 방향은 `Utility ← Core ← Product ← Market` 한 방향입니다.

- **Core**는 *어떻게 계산하는가*(수치 방법)만 담당하고, 행사가·콜/풋 같은 계약 조건은 모릅니다.
- **Product**는 *무엇을 계산하는가*(payoff, 행사 규칙)를 정의하고, payoff를 **함수 객체**로 Core 엔진에 넘깁니다.
  덕분에 같은 엔진으로 유러피안·아메리칸을 모두 계산하고, 새 상품은 payoff만 추가하면 됩니다.
- **Product**는 Market을 import하지 않습니다. 변동성·금리는 스칼라로 받습니다.
- **Market**은 Product의 가격식을 역으로 이용합니다. (예: `ImpVol`은 `EurOpt.VanillaOpt`를 Newton에 넘겨 σ를 역산)
- `Product`는 **평가 방법별 모듈**로 나뉘고, 모듈마다 같은 이름의 함수(`VanillaOpt`)를 둡니다. 모듈 이름으로 구분해서 호출합니다. (예: `EurOpt.VanillaOpt`, `AmeOpt.VanillaOpt`)

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
| `MarsagliaRnd(shape=1)` | Marsaglia polar method로 표준정규난수 배열 생성 (sin·cos 미사용) |
| `Cholesky(corr)` | 상관행렬을 하삼각행렬 $L$로 분해 ($\rho = LL^T$), 직접 구현 |

- `CND`: Abramowitz & Stegun (1964) 다항 근사, 오차 약 $10^{-7}$ 수준

$$N(x) \approx 1 - \phi(x)\,(a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5), \quad t = \frac{1}{1 + p\,|x|}$$

- `GenRnd`: ANSI C(Watcom) 파라미터 $X_{n+1} = (aX_n + c) \bmod m$, $a = 1103515245,\ c = 12345,\ m = 2^{31}$. 생성기 상태는 모듈 안에 유지되어 호출마다 이어지며, 초기 시드는 import 시점의 시각(μs)입니다. `SetSeed(42)`처럼 고정하면 같은 결과를 재현할 수 있습니다.
- `BoxMullerRnd`: 균등난수 $U_1, U_2$로부터

$$Z_1 = \sqrt{-2\ln U_1}\cos(2\pi U_2), \quad Z_2 = \sqrt{-2\ln U_1}\sin(2\pi U_2)$$

- `MarsagliaRnd`: $U \in (0,1)$을 $V = 2U - 1 \in (-1, 1)$로 바꾼 뒤, 단위원 안에 들어오는 점만 채택($0 < s < 1$)합니다. 기각되는 비율은 $1 - \pi/4 \approx 21\%$입니다.

$$s = V_1^2 + V_2^2, \quad Z_{1,2} = V_{1,2}\sqrt{\frac{-2\ln s}{s}}$$

- `Cholesky`: $\rho_{ij}$는 $L$의 i행과 j행의 내적이라는 점을 이용해, 위에서 아래로·왼쪽에서 오른쪽으로 한 원소씩 구합니다. 대각선에서 제곱근 안이 0 이하이면 양의 정부호가 아니므로 `ValueError`를 냅니다.
  - 3×3 손 계산 과정: [`Utility/숄레츠키분해_수기계산.jpg`](Utility/숄레츠키분해_수기계산.jpg)

### `Utility/Solver.py`

| 함수 | 설명 |
|---|---|
| `Newton(rootFunc, rootParam, target, tol=1e-6, maxTry=100)` | $f(x) = \text{target}$의 해를 Newton-Raphson으로 탐색 |
| `Bisection(rootFunc, target, low, high, tol=1e-6, maxTry=100)` | 구간 `[low, high]`에서 이분법으로 탐색 |

- 두 함수 모두 `rootFunc`는 **인자 하나를 받는 함수**입니다. 나머지 파라미터는 클로저로 고정해서 넘깁니다. (예: `ImpVol` 안의 `TheoPrice(sigma)`)
- `Newton`: 도함수를 따로 받지 않고 **중앙차분**으로 근사합니다. 스텝은 $h = \sqrt[3]{\varepsilon_{mach}}\cdot\max(|x|, 1) \approx 6\times10^{-6}\cdot\max(|x|, 1)$ (Nocedal & Wright, 2006)

$$f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}, \qquad x_{n+1} = x_n - \frac{f(x_n) - \text{target}}{f'(x_n)}$$

  - 기울기가 0에 가깝거나 `maxTry` 안에 수렴하지 않으면 `ValueError`
  - `tol`은 **함수값 오차** $|f(x) - \text{target}|$ 기준
- `Bisection`: 중간점과 왼쪽 끝의 부호를 비교해 구간을 절반씩 줄입니다. 증가·감소함수 모두 동작합니다.
  - 양 끝의 부호가 같으면(구간 안에 해가 없으면) `ValueError`
  - `tol`은 **구간 반폭** $(high - low)/2$ 기준
  - `low`, `high`에 기본값을 두지 않아 호출하는 쪽에서 구간을 명시합니다.

### `Core/Tree.py`

| 함수 | 설명 |
|---|---|
| `CRRTree(S, T, R, sigma, payoffFunc, Q=0.0, N=252, earlyExercise=False)` | Cox-Ross-Rubinstein (1979) 이항트리 |
| `BDTTree()` | Black-Derman-Toy (1990) 단기금리 트리 — 작업 예정 |

- `payoffFunc`: 주가(스칼라 또는 배열)를 받아 payoff를 돌려주는 **함수**. 호출 결과가 아니라 함수 자체를 넘깁니다.
- `earlyExercise=True`면 각 노드에서 `max(계속보유가치, 행사가치)`(아메리칸), `False`면 할인 기대값만 사용(유러피안)합니다.
- `N`은 **연간** 스텝 수이며, 총 스텝 수는 `round(N × T)`입니다. `T == 0`이면 `payoffFunc(S)`를 반환합니다.

$$u = e^{\sigma\sqrt{\Delta t}}, \quad d = 1/u, \quad p = \frac{e^{(R-Q)\Delta t} - d}{u - d}, \quad V_i = e^{-R\Delta t}\left[p\,V_{i+1}^{up} + (1-p)\,V_{i+1}^{down}\right]$$

### `Core/MC.py`

| 함수 | 설명 |
|---|---|
| `BlackScholes(S, T, R, sigma, corr=None, Q=None, N=252, numsSim=10_000)` | 단일/다자산 범용 GBM 경로 시뮬레이션 (상관계수 반영) |
| `GarmanKohlhagen(S, T, R_d, R_f, sigma, N=252, numsSim=10_000)` | 환율 경로 (`BlackScholes`에 `R=R_d`, `Q=R_f`로 위임) |
| `_BlackSholesSingle(...)` | 단일 자산 전용 (내부 테스트·비교용, 2차원 반환) |

**입력**

| 파라미터 | 형태 | 비고 |
|---|---|---|
| `S`, `sigma`, `Q` | 스칼라 또는 길이 n 배열 | 자산마다 다른 값. 스칼라는 길이 1 배열로 처리 |
| `corr` | n×n 상관행렬 | 다자산이면 필수, 단일 자산이면 생략 시 `[[1.0]]` |
| `R`, `T`, `N`, `numsSim` | 스칼라 | 모든 자산이 같은 할인율·시간축을 공유 |

**계산 과정**

1. 독립 표준정규난수 `Z`를 shape `(numsSim/2, step, n)`으로 생성 (`MarsagliaRnd`)
2. **Antithetic Variates**: $Z$와 $-Z$를 이어 붙여 분산 감소
3. **상관 부여**: `Z @ L.T` — 같은 시점의 자산끼리만 섞이고, 시점 간 독립성은 유지
4. 자산별 drift·변동성을 브로드캐스팅으로 적용하고 시간 축(`axis=1`)으로 누적

$$S^{(i)}_{t+\Delta t} = S^{(i)}_t \exp\left[\left(R - Q_i - \tfrac{1}{2}\sigma_i^2\right)\Delta t + \sigma_i\sqrt{\Delta t}\,W^{(i)}\right], \qquad W = LZ$$

- 반환값: shape `(numsSim, step + 1, n)`의 경로 배열 (첫 시점은 `S`), `step = round(T × N)`. **단일 자산도 3차원**입니다.
- 입력 검사: `S`, `sigma` ≤ 0 또는 `T` < 0, 배열 길이 불일치, `corr` 크기 불일치, 양의 정부호가 아닌 상관행렬이면 `ValueError`
- `numsSim`이 홀수면 antithetic 쌍 구조 때문에 경로가 `numsSim − 1`개 생성됩니다.
- FX의 `S`는 **외국 통화 1단위당 국내 통화 가격**입니다. (USD/KRW = 1,400이면 `R_d`=원화 금리, `R_f`=달러 금리)

### `Product/EurOpt.py`

| 함수 | 설명 |
|---|---|
| `VanillaOpt(S, K, T, sigma, R, Q=0.0, isCall=True)` | Black-Scholes(-Merton) / Garman-Kohlhagen 유러피안 옵션 |
| `DigitalOpt(S, K, T, sigma, R, cpn1, cpn2, Q=0.0)` | 디지털 옵션: 만기 주가가 `K` 초과면 `cpn2`, 이하면 `cpn1` 지급 |

- 주식과 FX가 같은 식을 공유합니다. FX 옵션은 `R` = 국내 금리, `Q` = 외국 금리로 넣습니다.
- 콜/풋은 `cpFlag`(콜 `+1`, 풋 `−1`)로 하나의 식에 통합했습니다.
- `T == 0`이면 내재가치(만기 지급액)를 반환합니다.
- 두 함수 모두 `(S, K, T, sigma, R, ...)` 순서로 인자를 받습니다.

$$d_1 = \frac{\ln(S/K) + (R - Q + \tfrac{1}{2}\sigma^2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

$$V_{vanilla} = \text{cpFlag}\cdot\left[S e^{-QT} N(\text{cpFlag}\cdot d_1) - K e^{-RT} N(\text{cpFlag}\cdot d_2)\right]$$

$$V_{digital} = e^{-RT}\left[\text{cpn2}\cdot N(d_2) + \text{cpn1}\cdot N(-d_2)\right]$$

### `Product/AmeOpt.py`

| 함수 | 설명 |
|---|---|
| `VanillaOpt(S, K, T, R, sigma, Q=0.0, isCall=True, N=252, isAmerican=True)` | `Core.Tree.CRRTree`로 계산하는 바닐라 옵션 (아메리칸/유러피안 선택) |

- 함수 안에서 `K`와 `cpFlag`를 기억하는 payoff 함수(클로저)를 만들어 `CRRTree`에 넘깁니다.
- `isAmerican=False`는 스텝 수를 늘릴수록 `EurOpt.VanillaOpt`로 수렴하므로, 두 방법을 서로 검증하는 데 쓸 수 있습니다.

### `Product/Fwd.py`

| 함수 | 설명 |
|---|---|
| `EquityFwd(S, T, R, Q=0.0, B=0.0)` | 주식 선도가격 (연속 배당수익률 `Q`, 대차 수수료율 `B`) |

$$F = S\,e^{(R - Q - B)T}$$

- 선도**가격**(Forward Price)이며, 계약 이후 손익인 선도**가치**(Forward Value)와는 다릅니다.

### `Market/Curve.py`

| 함수 | 설명 |
|---|---|
| `LoadDF(tenorArray, rateArray, targetTau)` | pillar 테너·연속복리 zero rate로부터 임의 만기의 할인계수 계산 |

- pillar(지표 테너)만 저장하고, 그 사이는 **zero rate 선형보간**합니다. 구간 밖은 양 끝 금리로 **flat 외삽**합니다.

$$r(\tau) = r_i + (r_{i+1} - r_i)\frac{\tau - \tau_i}{\tau_{i+1} - \tau_i}, \qquad DF(\tau) = e^{-r(\tau)\,\tau}$$

- 입력 배열은 **오름차순으로 정렬된 상태**를 가정합니다. (정렬은 데이터 호출 단계에서 처리)

### `Market/Vol.py`

| 함수 | 설명 |
|---|---|
| `ImpVol(OptPrice, S, K, T, R, Q=0.0, initVol=None, isCall=True)` | 유러피안 옵션 가격에서 Black-Scholes 내재변동성 역산 |
| `HistVol(priceArray, volType="SMA", window=252, decayFactor=0.94)` | 역사적 변동성 (SMA / EWMA) — 작업 중 |

- `initVol`을 생략하면 **Manaster & Koehler (1982)** 초기값을 씁니다. 옵션 가격을 σ의 함수로 보면 이 점이 변곡점(vega 최대점)이므로, 여기서 출발한 Newton은 단조롭게 수렴합니다. ATM($F \approx K$)이면 0.2를 씁니다.

$$\sigma_0 = \sqrt{\frac{2\,|\ln(F/K)|}{T}}, \qquad F = S\,e^{(R-Q)T}$$

- 계산 순서: `Newton` → 실패하면 `Bisection(low=1e-4, high=5.0)`
- 구한 σ에서 vega가 `1e-3`보다 작으면 가격이 σ에 거의 반응하지 않아 해가 신뢰할 수 없으므로 `ValueError`를 냅니다. (deep ITM/OTM, 만기 직전)

### `Market/Greeks.py`

| 함수 | 설명 |
|---|---|
| `Delta(S, K, T, sigma, R, Q=0.0, isCall=True)` | $\partial V / \partial S$ |
| `Gamma(S, K, T, sigma, R, Q=0.0)` | $\partial^2 V / \partial S^2$ (콜·풋 동일) |
| `Vega(S, K, T, sigma, R, Q=0.0)` | $\partial V / \partial \sigma$ (콜·풋 동일), `ImpVol`의 신뢰성 검사에 사용 |

$$\Delta_{call} = e^{-QT}N(d_1), \quad \Delta_{put} = e^{-QT}\left[N(d_1) - 1\right], \quad \Gamma = \frac{e^{-QT}\phi(d_1)}{S\sigma\sqrt{T}}, \quad \text{Vega} = S e^{-QT}\sqrt{T}\,\phi(d_1)$$

- 연속 배당수익률(FX는 외국 금리) `Q`의 할인 $e^{-QT}$를 모두 반영합니다.
- 만기(`T == 0`)에서 `Delta`는 payoff의 기울기를 반환합니다: 콜은 $S > K$면 1, 풋은 $S < K$면 −1, 그 외(ATM 포함)는 0
- `Gamma`는 만기에서 정의되지 않으므로(ATM에서 발산) `T <= 0`이면 `ValueError`를 냅니다.

### `DB/DBConn.py`

| 함수 | 설명 |
|---|---|
| `LoadDB(strQuery)` | MySQL에 쿼리를 보내 결과를 `pandas.DataFrame`으로 반환 |

- 접속 정보는 `DB/.env`에서 읽습니다. 이 파일은 `.gitignore`에 포함되어 **커밋되지 않습니다.**

  ```
  DB_HOST=
  DB_PORT=3306
  DB_USER=
  DB_PWD=
  DB_DATABASE=
  DB_CHARSET=utf8mb4
  ```
- OS 환경변수(`USER` 등)와 겹치지 않도록 `DB_` 접두사를 붙였습니다.
- import 시점이 아니라 `LoadDB`를 호출할 때만 연결하고, `with` 블록이 끝나면 연결을 닫습니다.

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
from Product import EurOpt, AmeOpt
from Product.Fwd import EquityFwd

# Black-Scholes
EurOpt.VanillaOpt(S=100, K=100, T=1.0, sigma=0.2, R=0.03)                 # 9.4134 (Call)
EurOpt.VanillaOpt(S=100, K=100, T=1.0, sigma=0.2, R=0.03, isCall=False)   # 6.4579 (Put)
EurOpt.DigitalOpt(S=100, K=100, T=1.0, sigma=0.2, R=0.03, cpn1=0, cpn2=10)  # 5.0457 (K 초과 시 10 지급)

# Garman-Kohlhagen (USD/KRW 1,400, 원화 3%, 달러 4.5%, 변동성 10%)
EurOpt.VanillaOpt(S=1400, K=1400, T=1.0, sigma=0.1, R=0.03, Q=0.045)                # 44.26 (Call)
EurOpt.VanillaOpt(S=1400, K=1400, T=1.0, sigma=0.1, R=0.03, Q=0.045, isCall=False)  # 64.49 (Put)

# 이항트리
AmeOpt.VanillaOpt(S=100, K=100, T=1.0, R=0.03, sigma=0.2, isCall=False)                            # 6.7392 (아메리칸 풋)
AmeOpt.VanillaOpt(S=100, K=100, T=1.0, R=0.03, sigma=0.2, isCall=False, isAmerican=False)          # 6.4501 (유러피안 풋)
AmeOpt.VanillaOpt(S=100, K=100, T=1.0, R=0.03, sigma=0.2, isCall=False, N=2000, isAmerican=False)  # 6.4570 → BS로 수렴

# 선도
EquityFwd(S=100, T=1.0, R=0.03, Q=0.01)   # 102.0201
```

```python
from Market.Vol import ImpVol
from Market.Greeks import Delta, Gamma, Vega
from Market.Curve import LoadDF

# 내재변동성: 가격 → σ 왕복
ImpVol(OptPrice=9.4134, S=100, K=100, T=1.0, R=0.03)   # ≈ 0.2000

# 그릭스
Delta(S=100, K=100, T=1.0, sigma=0.2, R=0.03)   # 0.5987
Gamma(S=100, K=100, T=1.0, sigma=0.2, R=0.03)   # 0.01933
Vega(S=100, K=100, T=1.0, sigma=0.2, R=0.03)    # 38.667 (σ 1.00 변화 기준)

# 할인계수
tenors = [0.25, 0.5, 1, 2, 3, 5]
rates  = [0.030, 0.031, 0.032, 0.033, 0.034, 0.035]
LoadDF(tenors, rates, 1.5)   # 0.95242  (1Y·2Y 사이 보간, r = 3.25%)
LoadDF(tenors, rates, 10)    # 0.70469  (5Y 이후 flat 외삽, r = 3.5%)
```

```python
from Utility.Solver import Newton, Bisection

# x^2 = 2
Newton(lambda x: x**2, rootParam=1.0, target=2.0)    # 1.414213562
Bisection(lambda x: x**2, target=2.0, low=0, high=2)  # 1.414213...
```

```python
from Utility.Math import SetSeed, Cholesky
from Core.MC import BlackScholes

corr = [[1.0, 0.5, 0.3],
        [0.5, 1.0, 0.4],
        [0.3, 0.4, 1.0]]

Cholesky(corr)
# [[1.0,    0.0,    0.0   ],
#  [0.5,    0.8660, 0.0   ],
#  [0.3,    0.2887, 0.9092]]

# 3자산 상관 경로 (시드 고정으로 재현 가능)
SetSeed(42)
paths = BlackScholes(S=[100, 50, 200], T=1.0, R=0.03, sigma=[0.2, 0.3, 0.25],
                     corr=corr, Q=[0.01, 0.0, 0.02])
paths.shape
# (10000, 253, 3)  ← (경로, 시점, 자산)
# 로그수익률 상관계수 ≈ 0.499 / 0.299 / 0.399

# 단일 자산은 corr 생략 가능
BlackScholes(100, 1.0, 0.03, 0.2, Q=0.01).shape
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
- `DB` 모듈 사용 시 추가: `pymysql`, `python-dotenv`, `pandas`
- 모든 import는 저장소 루트 기준입니다. 모듈 파일을 직접 실행할 때는 루트에서 `-m` 옵션을 사용하세요.
  ```bash
  python -m Core.MC        # O
  python Core/MC.py        # X: ModuleNotFoundError: No module named 'Utility'
  ```
- Python 3.13에서 테스트했습니다.

## TODO

- **금리**: BDT 트리(`BDTTree`) — 할인곡선 캘리브레이션(Arrow-Debreu 전진귀납 + Newton) 후 채권·금리옵션 평가
- **커브**: `Curve` 클래스, par swap 부트스트래핑, DB에서 커브 호출(`LoadCurve`)
- **채권**: `FixedBond`(가격·YTM·경과이자), 이산 쿠폰·dirty price 기반 `BondFwd`
- **선도**: `EquityFwd`에 이산 배당 차감 추가
- **변동성**: `HistVol`(SMA, EWMA) 완성
- **유한차분법**: `Core/FDM.py` Crank-Nicolson
- **몬테카를로**: 경로에 payoff 함수를 적용해 할인 평균을 내는 범용 프라이서, 스텝다운 ELS(낙인, 스노우볼 등)
- **날짜**: `Time2Mat`에 30/360 (2006 ISDA Definitions 4.16(f)) 지원
- **리스크**: Theta·Rho, Duration·Convexity, VaR
- **성능**: `BoxMullerRnd` / `MarsagliaRnd` 벡터화 (현재 Python 반복문 기반)

## License

[LICENSE](LICENSE) 참고
