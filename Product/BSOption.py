from Utility.Math import CND, log, sqrt, exp


def VanillaPayoff(S, K, T, R, sigma, Q=0.0, isCall=True):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if isCall:
        cpFlag = +1
    else:
        cpFlag = -1
    if T == 0:
        return max((S - K) * cpFlag, 0)
    elif T > 0:
        d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        return cpFlag * (
            S * exp(-Q * T) * CND(cpFlag * d1) - K * exp(-R * T) * CND(cpFlag * d2)
        )


def DigitalPayoff(S, K, T, R, sigma, cpn1, cpn2, Q=0.0):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if T == 0:
        return cpn2 if S > K else cpn1
    d2 = (log(S / K) + (R - Q - 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return exp(-R * T) * (cpn2 * CND(d2) + cpn1 * CND(-d2))
