from Core.Analytic import BSDigital, BSVanilla
from Utility.Date import Time2Mat


def VanillaOpt(S, K, startDate, expDate, sigma, R, Q=0.0, isCall=True, conv="ACT/365"):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv=conv)
    return BSVanilla(S=S, K=K, T=T, R=R, Q=Q, sigma=sigma, isCall=isCall)


def DigitalOpt(
    S,
    K,
    startDate,
    expDate,
    sigma,
    R,
    cpnLow,
    cpnHigh,
    Q=0.0,
    conv="ACT/365",
):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv=conv)
    return BSDigital(
        S=S,
        K=K,
        T=T,
        R=R,
        Q=Q,
        sigma=sigma,
        cpnLow=cpnLow,
        cpnHigh=cpnHigh,
    )
