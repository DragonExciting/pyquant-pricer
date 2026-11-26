from Utility.Solver import Newton, Bisection
from Utility.Math import exp, log, sqrt
from Product.EurOpt import VanillaOpt
from Market.Greeks import Vega


def ImpVol(OptPrice, S, K, T, R, Q=0.0, initVol=None, isCall=True):
    def TheoPrice(sigma):
        return VanillaOpt(S=S, K=K, T=T, sigma=sigma, R=R, Q=Q, isCall=isCall)

    if initVol == None:
        # The Calculation of Implied Variances from the Black-Scholes Model (Manaster & Koehler, 1982)
        # 블랙숄즈 옵션가격 공식을 sigma의 함수로 보면 변곡점이 정확히 하나 있고, 그 점에서 Newton을 시작하면 항상 단조롭게 수렴(2계 도함수 volga이용)
        F = S * exp((R - Q) * T)
        m = abs(log(F / K))
        initVol = sqrt(2 * m / T) if m > 1e-12 else 0.2  # ATM에서 0.2 사용

    try:
        impVol = Newton(
            rootFunc=TheoPrice,
            rootParam=initVol,
            target=OptPrice,
        )
    # 뉴튼랩슨으로 해찾고 실패할 경우, 이분법으로 해찾기
    except ValueError:
        impVol = Bisection(rootFunc=TheoPrice, target=OptPrice, low=1e-4, high=5.0)

    if Vega(S=S, K=K, T=T, R=R, Q=Q, sigma=impVol) < 1e-3:
        raise ValueError("Vega is too small")
    else:
        return impVol
