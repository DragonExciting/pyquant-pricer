from Utility.Math import CND, log, sqrt, exp

"""
FX Optiop - Garman–Kohlhagen model
https://en.wikipedia.org/wiki/Foreign_exchange_option 참고
"""


def VanillaPayoff(S, K, T, R_d, R_f, sigma, isCall=True):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if isCall:
        cpFlag = +1
    else:
        cpFlag = -1

    if T == 0:
        return max((S - K) * cpFlag, 0)
    elif T > 0:
        d1 = (log(S / K) + (R_d - R_f + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        return cpFlag * (
            S * exp(-R_f * T) * CND(cpFlag * d1) - K * exp(-R_d * T) * CND(cpFlag * d2)
        )
