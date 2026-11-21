from math import sqrt, pi, exp, cos, sin, log
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


def GenRnd():
    # Numerical Recipes (Knuth and H. W. Lewis, 1986)
    # 사용자 시드에 따른 난수생성 기능 추가 필요
    setSeed = int(time() * 1_000_000) % 2**32
    m = 2**32
    a = 1664525
    c = 1013904223
    rnd1 = (setSeed * a + c) % m
    rnd2 = (rnd1 * a + c) % m
    return max(rnd1 / m, 1e-8), max(rnd2 / m, 1e-8)


def BoxMullerRnd():
    # A Note on the Generation of Random Normal Deviates (Box & Muller, 1958)
    # 두개의 정규난수 반환
    uniRnd1, uniRnd2 = GenRnd()
    normRnd1 = sqrt(-2 * log(uniRnd1)) * cos(2 * pi * uniRnd2)
    normRnd2 = sqrt(-2 * log(uniRnd1)) * sin(2 * pi * uniRnd2)
    return normRnd1, normRnd2


if __name__ == "__main__":
    print(BoxMullerRnd())
    print(GenRnd())
