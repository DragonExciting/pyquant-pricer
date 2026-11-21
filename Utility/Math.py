from math import sqrt, pi, exp

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
    # 표준정규분포 누적분포함수 -> 블랙숄즈 방정식에 사용
    # Handbook of Mathematical Functions (Abramowitz & Stegun, 1964)
    absX = abs(x)
    t = 1 / (1 + p * absX)
    b = a1 * t + a2 * t**2 + a3 * t**3 + a4 * t**4 + a5 * t**5
    if x >= 0:
        return 1 - PDF(x) * b
    else:
        return PDF(-x) * b
