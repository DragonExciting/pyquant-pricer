from Core.Tree import CRRTree
from numpy import maximum


def VanillaPayoff(S, K, T, R, sigma, Q=0.0, isCall=True, N=252, isAmerican=True):
    if isCall:
        cpFlag = +1
    else:
        cpFlag = -1

    def Payoff(price):
        return maximum(cpFlag * (price - K), 0.0)

    # FuncPayoff()가 아닌 FuncPayoff로 CRRTree에 넘겨서 객체 자체를 넘기도록 함
    return CRRTree(
        S=S,
        T=T,
        R=R,
        sigma=sigma,
        FuncPayoff=Payoff,
        Q=Q,
        N=N,
        earlyExercise=isAmerican,
    )
