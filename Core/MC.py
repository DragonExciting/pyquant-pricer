from Utility.Math import BoxMullerRnd, sqrt, exp, Cholesky
from numpy import vstack, cumsum, hstack, zeros, asarray, concatenate, atleast_1d

"""
몬테 카를로 시뮬레이션
https://en.wikipedia.org/wiki/Monte_Carlo_method 참고

"""


# 단일 기초자산 블랙숄즈 기반 몬테카를로 시뮬레이션(테스트용)
def BlackSholesSingle(S, T, R, sigma, Q=0.0, N=252, numsSim=10_000):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    totalStep = max(int(round(T * N)), 1)
    dT = T / totalStep
    half = numsSim // 2
    # 분산감소기법: Antithetic
    rndSpace = BoxMullerRnd((half, totalStep))
    antithetic = vstack((rndSpace, -rndSpace))
    # 로그 수익률을 사용하여 블랙숄즈 변화분을 덧셈 형태로 변환
    logReturn = (R - Q - 0.5 * sigma**2) * dT + sigma * sqrt(dT) * antithetic
    logPath = hstack([zeros([(half * 2), 1]), cumsum(logReturn, axis=1)])
    path = S * exp(logPath)
    return path


# 단일/멀티 범용 블랙숄즈 기반 몬테카를로 시뮬레이션
def BlackScholes(S, T, R, sigma, corr=None, Q=None, N=252, numsSim=10_000):

    S = atleast_1d(
        asarray(S, float)
    )  # 스칼라로 인풋 받더라도 최소한 1차원 배열로 인식하게 수정
    sigma = atleast_1d(asarray(sigma, float))
    assetNums = len(S)

    if corr is None:
        if assetNums != 1:
            raise ValueError("Multi-Assets need correlation matrix")
        corr = [[1.0]]
        # 단일자산에 대해서는 상관계수 매트릭스 = [[1.0]] 설정
    if Q is None:
        Q = zeros(assetNums)
    else:
        Q = atleast_1d(asarray(Q, float))

    # 파라미터 검증 구간
    if (sigma <= 0).any() or (S <= 0).any() or T < 0:
        raise ValueError("Incorrect Input")

    if len(sigma) != assetNums or len(Q) != assetNums:
        raise ValueError("S, sigma, Q must have the same length")

    if assetNums > 1 and asarray(corr).shape != (assetNums, assetNums):
        raise ValueError("Corr must be (n, n) matrix")

    L = Cholesky(corr=corr)

    totalStep = max(int(round(T * N)), 1)
    dT = T / totalStep
    half = numsSim // 2
    # 분산감소기법: Antithetic
    rndSpace = BoxMullerRnd((half, totalStep, assetNums))
    antithetic = concatenate([rndSpace, -rndSpace])
    corrAntithetic = antithetic @ L.T

    # 로그 수익률을 사용하여 블랙숄즈 변화분을 덧셈 형태로 변환
    logReturn = (R - Q - 0.5 * sigma**2) * dT + sigma * sqrt(dT) * corrAntithetic
    logPath = concatenate(
        [
            zeros([(half * 2), 1, assetNums]),
            cumsum(logReturn, axis=1),
        ],
        axis=1,
    )
    path = S * exp(logPath)
    return path


# Garman–Kohlhagen 기반 몬테카를로 시뮬레이션
def GarmanKohlhagen(S, T, R_d, R_f, sigma, N=252, numsSim=10_000):
    path = BlackScholes(S=S, T=T, R=R_d, sigma=sigma, Q=R_f, N=N, numsSim=numsSim)
    return path
