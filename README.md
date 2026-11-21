# QuantProject

Python으로 직접 구현하는 금융상품 프라이싱 및 리스크 라이브러리입니다.
날짜 관례, 시장 데이터, 상품 평가, 리스크 측정까지 단계적으로 구현하며 금융공학을 공부한 기록입니다.

## 구조

| 모듈 | 역할 | 상태 |
|---|---|---|
| `Utility` | 날짜 변환, Day Count Convention, 쿠폰 스케줄, 정규분포 함수 | 진행 중 |
| `Core` | 프라이싱 엔진 공통 기반 | 예정 |
| `Market` | 금리 커브, 변동성 등 시장 데이터 | 예정 |
| `Product` | 채권, 옵션 등 개별 상품 평가 | 예정 |
| `Risk` | 민감도(Greeks, Duration), VaR | 예정 |

## 구현된 기능

### `Utility/Date.py`
- `ConvDate`: `20240115`, `"20240115"`, `"2024-01-15"` 형식을 `datetime.date`로 변환
- `TimeToMaturity`: 두 날짜 사이의 연 단위 기간 계산
  - `"365"`: ACT/365 Fixed
  - `"360"`: ACT/360
  - `"ACT"`: ACT/ACT (ISDA) — 연도별 실제 일수(윤년 포함)로 나눠 합산
- `MakeSchedule`: 쿠폰 지급 스케줄 생성
  - 만기일에서 역산하여 생성하므로 월말 날짜가 밀리지 않음 (1/31 → 2/29 → 3/31)
  - 연 지급 횟수 1, 2, 4, 6, 12회 지원
  - Stub 처리: `"S"`(Short front stub), `"L"`(Long front stub)

### `Utility/Math.py`
- `PDF`: 표준정규분포 확률밀도함수
- `CND`: 표준정규분포 누적분포함수
  - Abramowitz & Stegun (1964) 다항 근사, 오차 약 $10^{-7}$ 수준

$$N(x) \approx 1 - \phi(x)\,(a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5), \quad t = \frac{1}{1 + p\,|x|}$$

## 사용 예시

```python
from Utility.Date import MakeSchedule, TimeToMaturity
from Utility.Math import CND

# 3년 만기, 분기 지급, 시작일이 쿠폰일과 어긋나는 경우 (Short front stub)
MakeSchedule(20240301, 20270115, 4, stub="S")[:3]
# [date(2024, 3, 1), date(2024, 4, 15), date(2024, 7, 15)]

# ACT/ACT ISDA: 184/366 + 181/365
TimeToMaturity("2024-07-01", 20250701, conv="ACT")
# 0.99862...

CND(1.96)
# 0.97500...
```

## 설치

```bash
pip install -r requirements.txt
```

Python 3.13에서 테스트했습니다.
