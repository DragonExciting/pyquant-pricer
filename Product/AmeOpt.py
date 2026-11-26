from Core.Tree import CRRTree
from Utility.Date import Time2Mat
from numpy import maximum


def VanillaOpt(
    S, K, startDate, expDate, R, sigma, Q=0.0, isCall=True, N=252, isAmerican=True
):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv="ACT/365")
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
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
        payoffFunc=Payoff,
        Q=Q,
        N=N,
        earlyExercise=isAmerican,
    )
