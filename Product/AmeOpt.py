from Core.Tree import CRRTree
from Utility.Date import Time2Mat
from numpy import maximum, where


def VanillaOpt(
    S,
    K,
    startDate,
    expDate,
    R,
    sigma,
    Q=0.0,
    isCall=True,
    N=252,
    isAmerican=True,
    conv="ACT/365",
):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv=conv)
    if T is None:
        raise ValueError("Incorrect Input")
    if sigma <= 0 or S <= 0 or T < 0 or K <= 0:
        raise ValueError("Incorrect Input")
    if isCall:
        cpFlag = +1
    else:
        cpFlag = -1

    def Payoff(price):
        return maximum(cpFlag * (price - K), 0.0)

    # FuncPayoff()가 아닌 payoffFunc로 CRRTree에 넘겨서 객체 자체를 넘기도록 함
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


def DigitalOpt(
    S, K, startDate, expDate, sigma, R, cpnLow, cpnHigh, Q=0.0, N=252, isAmerican=True
):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv="ACT/365")
    if T is None:
        raise ValueError("Incorrect Input")
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")

    def Payoff(price):
        return where(price > K, cpnHigh, cpnLow)
        # 배열에서 인식하기위해서 where사용

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
