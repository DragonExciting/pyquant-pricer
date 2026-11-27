from time import time

from numba import vectorize
from numpy import array, cos, exp, log, pi, prod, sin, sqrt, zeros


def PDF(x):
    # 표준정규분포 밀도함수 -> 누적분포함수 계산에 사용
    return exp(-0.5 * x**2) / (sqrt(2 * pi))


def CND(x):
    # 표준정규분포 누적분포함수 근사공식
    # Handbook of Mathematical Functions (Abramowitz & Stegun, 1964)
    p = 0.2316419
    a1 = 0.319381530
    a2 = -0.356563782
    a3 = 1.781477937
    a4 = -1.821255978
    a5 = 1.330274429
    absX = abs(x)
    t = 1 / (1 + p * absX)
    b = a1 * t + a2 * t**2 + a3 * t**3 + a4 * t**4 + a5 * t**5
    if x >= 0:
        return 1 - PDF(x) * b
    else:
        return PDF(-x) * b


"""
유사난수: 컴퓨터는 무작위성이 개입되지 않도록 설계된 계산기이므로 진정난수 생성불가
          그러므로 유사난수를 생성하는 알고리즘 개발

진정난수 특징
    1. 예측 불가능성
    2. 무편향성
    3. 무관성
    -> 전자기적인 불규칙 노이즈 등을 파악하는 하드웨어 추가 필요

선형난수생성기    
https://en.wikipedia.org/wiki/Linear_congruential_generator 참고

박스-뮬러 변환
https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform 참고
"""


# 선형합동생성기 상태: 호출 사이에 이어져야 난수열이 독립적으로 생성됨
# _접두사를 붙이면 import * 전체 호출에서 가져오지 않음. _a로 개별 호출하면 불러와짐
_m = 2**31
_a = 1103515245
_c = 12345
_initNum = int(time() * 1_000_000) % _m


def SetSeed(seed=None):
    # seed=None이면 현재 시각으로 초기화, 정수를 주면 재현 가능한 난수열 생성
    global _initNum
    if seed is None:
        seed = int(time() * 1_000_000)
    _initNum = int(seed) % _m


def GenRnd():
    # ANSI C: Watcom
    global _initNum
    _initNum = (_a * _initNum + _c) % _m
    rnd1 = _initNum / _m
    _initNum = (_a * _initNum + _c) % _m
    rnd2 = _initNum / _m
    # 0~1 사이의 난수만 반환
    return max(rnd1, 1e-8), max(rnd2, 1e-8)


def BoxMullerRnd(shape: int | tuple[int, ...] = 1):
    # A Note on the Generation of Random Normal Deviates (Box & Muller, 1958)
    # 사용자가 원하는 Numpy array 형태로 정규난수 반환
    # MC에서 데이터 타입 밑줄 뜨기때문에 정수와 튜플 모두 인식한다는걸 타입 힌트로 명시
    if isinstance(shape, int):
        shape = (shape,)  # 쉼표를 넣어야 튜플형태로 인식함
    else:
        shape = tuple(shape)
    N = prod(shape)  # 생성해야할 총 난수
    nPair = (N + 1) // 2  # 생성해야할 총 횟수(2개씩 생성, 홀수면 1쌍 추가)

    rndSpace = []
    for _ in range(nPair):
        uniRnd1, uniRnd2 = GenRnd()

        normRnd1 = sqrt(-2 * log(uniRnd1)) * cos(2 * pi * uniRnd2)
        normRnd2 = sqrt(-2 * log(uniRnd1)) * sin(2 * pi * uniRnd2)
        rndSpace.append((normRnd1, normRnd2))
    rndArray = array(rndSpace).ravel()[:N].reshape(shape)
    # .ravel() 1차원으로 펼침
    # N이 홀수인 경우, 생성된 쌍은 N+1개 이므로 [:N]을 통해 마지막 1개를 제거해야 reshape에서 오류 미발생
    return rndArray


def MarsagliaRnd(shape: int | tuple[int, ...] = 1):
    # https://en.wikipedia.org/wiki/Marsaglia_polar_method
    # A Convenient Method for Generating Normal Variables (Marsaglia, 1964)

    # sin, cos 미사용
    if isinstance(shape, int):
        shape = (shape,)  # 쉼표를 넣어야 튜플형태로 인식함
    else:
        shape = tuple(shape)
    N = prod(shape)  # 생성해야할 총 난수
    nPair = (N + 1) // 2  # 생성해야할 총 횟수(2개씩 생성, 홀수면 1쌍 추가)

    rndSpace = []
    for _ in range(nPair):
        uniRnd1, uniRnd2 = GenRnd()
        uniRnd1, uniRnd2 = 2 * uniRnd1 - 1, 2 * uniRnd2 - 1
        # 마르살리아 알고리즘은 -1 ~ 1 사이의 난수를 사용함
        # (0, 1) -> (0, 2) -> (-1, 1) 형식으로 난수범위 변환
        s = uniRnd1**2 + uniRnd2**2
        while s >= 1 or s <= 0:
            uniRnd1, uniRnd2 = GenRnd()
            uniRnd1, uniRnd2 = 2 * uniRnd1 - 1, 2 * uniRnd2 - 1
            s = uniRnd1**2 + uniRnd2**2

        k = sqrt(-2 * log(s) / s)
        normRnd1 = k * uniRnd1
        normRnd2 = k * uniRnd2
        rndSpace.append((normRnd1, normRnd2))
    rndArray = array(rndSpace).ravel()[:N].reshape(shape)
    # .ravel() 1차원으로 펼침
    # N이 홀수인 경우, 생성된 쌍은 N+1개 이므로 [:N]을 통해 마지막 1개를 제거해야 reshape에서 오류 미발생
    return rndArray


"""
Inverse CDF -> Quasi-MC(Sobol)에 사용

CDF: z이하일 확률을 돌려주는 함수
CDF^(-1): 확률 p에 해당하는 분위수(z)를 반환하는 함수 -> 차원을 뒤섞지 않기에 저불일치 특성이 유지됨

The Full Monte (Moro, 1995) 근사법 사용
Inverse CDF는 닫힌해가 없기때문에 유리함수 근사 사용
"""

_a0 = 2.50662823884
_a1 = -18.61500062529
_a2 = 41.39119773534
_a3 = -25.44106049637
_b0 = -8.47351093090
_b1 = 23.08336743743
_b2 = -21.06224101826
_b3 = 3.13082909833
_c0 = 0.3374754822726147
_c1 = 0.9761690190917186
_c2 = 0.1607979714918209
_c3 = 0.0276438810333863
_c4 = 0.0038405729373609
_c5 = 0.0003951896511919
_c6 = 0.0000321767881768
_c7 = 0.0000002888167364
_c8 = 0.0000003960315187


# @vectorize: 스칼라만 받는 함수를 numpy ufunc로 바꿔서 배열도 받을 수 있게 변환시켜줌
@vectorize(["float64(float64)"])
def InvCDF(uniRnd):
    if not (0 < uniRnd < 1):
        raise ValueError("Uniform Random Numbers must not be 0 or 1")
    y = uniRnd - 0.5
    if abs(y) < 0.42:
        r = y**2
        x = (
            y
            * (_a0 + _a1 * r + _a2 * r**2 + _a3 * r**3)
            / (1 + _b0 * r + _b1 * r**2 + _b2 * r**3 + _b3 * r**4)
        )
        return x
    else:
        r = log(-log(min(uniRnd, 1 - uniRnd)))
        x = (
            _c0
            + _c1 * r
            + _c2 * r**2
            + _c3 * r**3
            + _c4 * r**4
            + _c5 * r**5
            + _c6 * r**6
            + _c7 * r**7
            + _c8 * r**8
        )
        if uniRnd < 0.5:
            return -x
        else:
            return x


"""
상관행렬을 하삼각행렬로 분해: corr = L * L^T

2자산 예시:
    W_1 = Z_1
    W_2 = rho Z_1 + sqrt{1-rho^2} Z_2

행렬의 대각선(i = j): sqrt(원래값 - 지금까지 구한 같은 행 원소들의 제곱합)
대각선 아래(i > j)  : (원래값 - i행과 j행에서 이미 구한 부분의 내적)÷l_jj


숄레츠키 분해
https://en.wikipedia.org/wiki/Cholesky_decomposition 참고
"""


# 다자산용 숄레츠키 분해
def Cholesky(corr):
    n = len(corr)
    L = zeros((n, n))

    for i in range(n):  # 행: 위에서 아래로
        for j in range(i + 1):  # 열: 왼쪽부터 대각선까지
            s = corr[i][j] - L[i, :j] @ L[j, :j]
            # L^T의 j열 = L의 j행 -> corr[i][j] 원소는 L의 i행과 j행의 내적
            if i == j:
                if s <= 0:
                    # 양의 정부호 확인
                    raise ValueError("Correlation matrix is not positive definite")
                L[i, j] = sqrt(s)
            else:
                L[i, j] = s / L[j, j]
    return L
