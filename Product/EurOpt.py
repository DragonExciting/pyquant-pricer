from Core.Analytic import BSVanilla
from Utility.Date import Time2Mat


def VanillaOpt(S, K, startDate, expDate, sigma, R, Q=0.0, isCall=True, conv="ACT/365"):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv=conv)
    return BSVanilla(S=S, K=K, T=T, R=R, Q=Q, sigma=sigma, isCall=isCall)
