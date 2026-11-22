from numpy import (
    array,
    cumsum,
    hstack,
    vstack,
    sqrt,
    pi,
    exp,
    cos,
    sin,
    log,
    prod,
    zeros,
)
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
m = 2**31
a = 1103515245
c = 12345
initNum = int(time() * 1_000_000) % m


def SetSeed(seed=None):
    # seed=None이면 현재 시각(μs)으로 초기화, 정수를 주면 재현 가능한 난수열 생성
    global initNum
    if seed is None:
        seed = int(time() * 1_000_000)
    initNum = int(seed) % m


def GenRnd():
    # ANSI C: Watcom
    global _lcgState
    _lcgState = (a * initNum + c) % m
    rnd1 = initNum / m
    _lcgState = (a * initNum + c) % m
    rnd2 = _lcgState / m
    return max(rnd1, 1e-8), max(rnd2, 1e-8)


def BoxMullerRnd(shape=1):
    # A Note on the Generation of Random Normal Deviates (Box & Muller, 1958)
    # 사용자가 원하는 Numpy array 형태로 정규난수 반환
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


"""
몬테 카를로 시뮬레이션
https://en.wikipedia.org/wiki/Monte_Carlo_method 참고

숄레츠키 분해
https://en.wikipedia.org/wiki/Cholesky_decomposition 참고
"""


# 블랙숄즈 기반 몬테카를로 시뮬레이션
def SingleMC(S, T, R, sigma, Q=0.0, N=252, numsSim=10_000):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    totalStep = max(int(round(T * N)), 1)
    dT = T / totalStep
    # 분산감소기법: Antithetic
    rndSpace = BoxMullerRnd((int(numsSim / 2), totalStep))
    antiSpace = -rndSpace
    antithetic = vstack((rndSpace, antiSpace))
    # 로그 수익률을 사용하여 블랙숄즈 변화분을 덧셈 형태로 변환
    logReturn = (R - Q - 0.5 * sigma**2) * dT + sigma * sqrt(dT) * antithetic
    logPath = hstack([zeros([(int(numsSim / 2) * 2), 1]), cumsum(logReturn, axis=1)])
    path = S * exp(logPath)
    return path


if __name__ == "__main__":
    print(SingleMC(100, 1.0, 0.03, 0.2))
