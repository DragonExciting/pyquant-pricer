from Utility.Math import CND, log, sqrt, exp
from Core.Tree import CRRTree
from numpy import maximum


def BSOption(S, K, T, R, sigma, Q=0.0, isCall=True):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if isCall:
        cpFlag = +1
    else:
        cpFlag = -1
    if T == 0:
        return max((S - K) * cpFlag, 0)
    elif T > 0:
        d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        return cpFlag * (
            S * exp(-Q * T) * CND(cpFlag * d1) - K * exp(-R * T) * CND(cpFlag * d2)
        )


def BinomialOption(S, K, T, R, sigma, Q=0.0, isCall=True, N=252, isAmerican=True):
    if isCall:
        cpFlag = +1
    else:
        cpFlag = -1

    def FuncPayoff(price):
        return maximum(cpFlag * (price - K), 0.0)

    # FuncPayoff()가 아닌 FuncPayoff로 CRRTree에 넘겨서 객체 자체를 넘기도록 함
    return CRRTree(
        S=S,
        T=T,
        R=R,
        sigma=sigma,
        FuncPayoff=FuncPayoff,
        Q=Q,
        N=N,
        earlyExercise=isAmerican,
    )
