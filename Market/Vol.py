from Core.Analytic import BSVanilla
from Market.Greeks import BSVega
from Utility.Date import Time2Mat
from Utility.Math import exp, log, sqrt
from Utility.Solver import Bisection, Newton


def ImpVol(
    OptPrice,
    S,
    K,
    startDate,
    expDate,
    R,
    Q=0.0,
    initVol=None,
    isCall=True,
    conv="ACT/365",
):
    T = Time2Mat(startDate, expDate, conv=conv)
    if T <= 0 or T == None:
        raise ValueError("Incorrect Input")

    def _TheoPrice(sigma):
        return BSVanilla(
            S=S,
            K=K,
            T=T,
            sigma=sigma,
            R=R,
            Q=Q,
            isCall=isCall,
        )

    if initVol == None:
        # The Calculation of Implied Variances from the Black-Scholes Model (Manaster & Koehler, 1982)
        # 블랙숄즈 옵션가격 공식을 sigma의 함수로 보면 변곡점이 정확히 하나 있고, 그 점에서 Newton을 시작하면 항상 단조롭게 수렴(2계 도함수 volga이용)
        F = S * exp((R - Q) * T)
        m = abs(log(F / K))
        initVol = sqrt(2 * m / T) if m > 1e-12 else 0.2  # ATM에서 0.2 사용

    try:
        impVol = Newton(
            rootFunc=_TheoPrice,
            rootParam=initVol,
            target=OptPrice,
        )
    # 뉴튼랩슨으로 해찾고 실패할 경우, 이분법으로 해찾기
    except ValueError:
        impVol = Bisection(rootFunc=_TheoPrice, target=OptPrice, low=1e-4, high=5.0)

    if BSVega(S=S, K=K, T=T, R=R, Q=Q, sigma=impVol) < 1e-3:
        raise ValueError("Vega is too small")
    else:
        return impVol


"""
SABR volatility model -> Shifted Model로 구축할 예정
https://en.wikipedia.org/wiki/SABR_volatility_model
"""


def SABR():
    return


def Heston():
    return
