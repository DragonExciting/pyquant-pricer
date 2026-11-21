from math import sqrt, pi, exp, cos, sin, log
from random import random


def PDF(x):
    # 표준정규분포 밀도함수 -> 누적분포함수 계산에 사용
    return exp(-0.5 * x**2) / (sqrt(2 * pi))


def CND(x):
    # 표준정규분포 누적분포함수 근사공식
    # Handbook of Mathematical Functions (Abramowitz & Stegun, 1964) 참고
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

random.random -> [0,1)의 균등난수 생성
"""


def BoxMullerRnd():
    # A Note on the Generation of Random Normal Deviates (Box & Muller, 1958) 참고
    # 두개의 정규난수 반환
    uniRnd1 = random()
    uniRnd2 = random()
    while uniRnd1 == 0:
        # log(0)은 ValueError 유발
        uniRnd1 = random()
    normRnd1 = sqrt(-2 * log(uniRnd1)) * cos(2 * pi * uniRnd2)
    normRnd2 = sqrt(-2 * log(uniRnd1)) * sin(2 * pi * uniRnd2)
    return normRnd1, normRnd2


if __name__ == "__main__":
    print(BoxMullerRnd())
