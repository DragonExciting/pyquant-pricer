from math import sqrt, pi, exp
from random import uniform

p = 0.2316419
a1 = 0.319381530
a2 = -0.356563782
a3 = 1.781477937
a4 = -1.821255978
a5 = 1.330274429


def PDF(x):
    # 표준정규분포 밀도함수 -> 누적분포함수 계산에 사용
    return exp(-0.5 * x**2) / (sqrt(2 * pi))


def CND(x):
    # 표준정규분포 누적분포함수
    # Handbook of Mathematical Functions (Abramowitz & Stegun, 1964) 참고
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
-> 전자기적인 불규칙 노이즈 등을 파악하는 하드웨어가 추가 필요
"""

def NormRnd():
    # A Convenient Method for Generating Normal Variables (Marsaglia, 1964) 참고
    


if __name__ == "__main__":
    print(uniform(0, 1))
