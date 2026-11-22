from ..Utility.Math import CND, log, sqrt, exp
from numpy import arange, maximum


def EuropeanOption(S, K, T, R, sigma, Q=0.0, isCall=True):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if T == 0:
        if isCall:
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    elif T > 0:
        d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        if isCall:
            return S * exp(-Q * T) * CND(d1) - K * exp(-R * T) * CND(d2)
        else:
            return K * exp(-R * T) * CND(-d2) - S * exp(-Q * T) * CND(-d1)
    else:
        raise ValueError("Option Expiration")


def AmericanOption(S, K, T, R, sigma, Q=0.0, isCall=True, N=252):
    # Option pricing: A simplified approach (Cox & Ross & Rubinstein, 1979)
    if sigma <= 0 or S <= 0 or N <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if T == 0:
        if isCall:
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    elif T > 0:
        dT = T / N
        u = exp(sigma * sqrt(dT))
        d = 1 / u
        p = (exp((R - Q) * dT) - d) / (u - d)
        df = exp(-R * dT)  # 할인계수

        j = arange(
            N + 1
        )  # j = 상승 횟수 0 ~ N, arange: 균등간격 1차원 넘파이 배열 반환
        if isCall:
            optValue = maximum(S * u**j * d ** (N - j) - K, 0.0)
        else:
            optValue = maximum(K - S * u**j * d ** (N - j), 0.0)
            # 만기시점의 옵션 가치

        for i in range(N - 1, -1, -1):
            # Backward Induction
            j = arange(i + 1)
            Si = S * u**j * d ** (i - j)
            contValue = df * (p * optValue[1 : i + 2] + (1 - p) * optValue[0 : i + 1])
            if isCall:
                excerciseValue = maximum(Si - K, 0.0)
            else:
                excerciseValue = maximum(K - Si, 0.0)

            optValue = maximum(contValue, excerciseValue)

        return optValue[0]
