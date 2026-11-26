from Utility.Solver import Newton, Bisection
from Utility.Math import exp, log, sqrt
from Product.EurOpt import VanillaPayoff
from Market.Greeks import Vega


def ImpVol(OptPrice, S, K, T, R, Q=0.0, initVol=None, isCall=True):
    def TheoPrice(sigma):
        return VanillaPayoff(S=S, K=K, T=T, sigma=sigma, R=R, Q=Q, isCall=isCall)

    if initVol == None:
        # Manaster-Koehler 초기값 이용
        # 블랙숄즈 기반의 모형에서 뉴튼-랩슨으로 내재변동성 역산할때, 전역 수렴을 보장하는 최적의 시작점
        F = S * exp((R - Q) * T)
        m = abs(log(F / K))
        initVol = sqrt(2 * m / T) if m > 1e-12 else 0.2  # ATM에서 0.2 사용

    try:
        impVol = Newton(
            rootFunc=TheoPrice,
            rootParam=initVol,
            target=OptPrice,
        )

    except ValueError:
        impVol = Bisection(rootFunc=TheoPrice, target=OptPrice, low=1e-4, high=5.0)

    if Vega(S=S, K=K, T=T, R=R, Q=Q, sigma=impVol) < 1e-3:
        raise ValueError("Vega is too small")
    else:
        return impVol
