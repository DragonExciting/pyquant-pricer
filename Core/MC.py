from Utility.Math import BoxMullerRnd, sqrt, exp
from numpy import vstack, cumsum, hstack, zeros

"""
몬테 카를로 시뮬레이션
https://en.wikipedia.org/wiki/Monte_Carlo_method 참고

숄레츠키 분해
https://en.wikipedia.org/wiki/Cholesky_decomposition 참고
"""


# 단일 기초자산 블랙숄즈 기반 몬테카를로 시뮬레이션(테스트용)
def EQSingleMonteCarlo(S, T, R, sigma, Q=0.0, N=252, numsSim=10_000):
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


"""
상관행렬을 하삼각행렬로 분해: corr = L L^T

2자산 예시:
    W_1 = Z_1
    W_2 = \rho Z_1 + \sqrt{1-\rho^2} Z_2
"""
# 다자산 범용 몬테카를로 시뮬레이션 - 숄레츠키 분해 적용(파라미터로 상관계수 행렬 추가)
def Cholesky(corr):






# Garman–Kohlhagen 기반 몬테카를로 시뮬레이션
def FXMonteCarlo(S, T, R_d, R_f, sigma, N=252, numsSim=10_000):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    totalStep = max(int(round(T * N)), 1)
    dT = T / totalStep
    # 분산감소기법: Antithetic
    rndSpace = BoxMullerRnd((int(numsSim / 2), totalStep))
    antiSpace = -rndSpace
    antithetic = vstack((rndSpace, antiSpace))
    # 로그 수익률을 사용하여 블랙숄즈 변화분을 덧셈 형태로 변환
    logReturn = (R_d - R_f - 0.5 * sigma**2) * dT + sigma * sqrt(dT) * antithetic
    logPath = hstack([zeros([(int(numsSim / 2) * 2), 1]), cumsum(logReturn, axis=1)])
    path = S * exp(logPath)
    return path
