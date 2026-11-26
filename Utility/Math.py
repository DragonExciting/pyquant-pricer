from numpy import array, sqrt, pi, exp, cos, sin, log, prod, zeros
from time import time


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


r"""
상관행렬을 하삼각행렬로 분해: corr = L L^T

2자산 예시:
    W_1 = Z_1
    W_2 = \rho Z_1 + \sqrt{1-\rho^2} Z_2

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
