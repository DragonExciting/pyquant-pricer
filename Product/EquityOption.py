from ..Utility.Math import CND, log, sqrt, exp


def VanillaOption(S, K, T, R, sigma, Q=0.0, isCall=True):
    if sigma <= 0 or S <= 0:
        raise ValueError("Incorrect Input")
    if 0 <= T < 0.000001:
        if isCall:
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    elif T > 0.000001:
        d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        if isCall:
            return S * exp(-Q * T) * CND(d1) - K * exp(-R * T) * CND(d2)
        else:
            return K * exp(-R * T) * CND(-d2) - S * exp(-Q * T) * CND(-d1)
    else:
        raise ValueError("Option Expiration")
