from Utility.Math import exp, sqrt
from numpy import arange, maximum

"""
Cox, Ross and Rubinstein in 1979
https://en.wikipedia.org/wiki/Binomial_options_pricing_model
"""


def CRRTree(S, T, R, sigma, payoffFunc, Q=0.0, N=252, earlyExercise=False):
    # Option pricing: A simplified approach (Cox & Ross & Rubinstein, 1979)
    if sigma <= 0 or S <= 0 or N <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    elif T == 0:
        return payoffFunc(S)
    elif T > 0:
        step = max(int(round(N * T)), 1)
        dT = T / step
        u = exp(sigma * sqrt(dT))
        d = 1 / u
        p = (exp((R - Q) * dT) - d) / (u - d)
        df = exp(-R * dT)  # 할인계수

        j = arange(step + 1)
        # j = 상승 횟수 0 ~ N, arange: 균등간격 1차원 넘파이 배열 반환
        matValue = S * u**j * d ** (step - j)
        optValue = payoffFunc(matValue)
        for i in range(step - 1, -1, -1):
            # Backward Induction
            j = arange(i + 1)
            Si = S * u**j * d ** (i - j)
            contValue = df * (p * optValue[1 : i + 2] + (1 - p) * optValue[0 : i + 1])
            if earlyExercise:
                # 아메리칸
                excerciseValue = payoffFunc(Si)
                optValue = maximum(contValue, excerciseValue)
            else:
                # 유러피안
                optValue = contValue

        return optValue[0]


"""
Black–Derman–Toy model
https://en.wikipedia.org/wiki/Black%E2%80%93Derman%E2%80%93Toy_model
"""
