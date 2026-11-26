from Utility.Math import CND, log, sqrt, exp
from Utility.Date import Time2Mat

"""
유러피언 바닐라 옵션에 대하여 주식, FX 공용으로 사용
주식: 블랙숄즈 닫힌 해
외환: Garman-Kohlhagen 닫힌 해
https://en.wikipedia.org/wiki/Foreign_exchange_option 참고
"""


def VanillaOpt(S, K, startDate, expDate, sigma, R, Q=0.0, isCall=True):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv="ACT/365")
    # FX Option으로 사용할 경우, R = 국내 금리, Q = 해외 금리
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


def DigitalOpt(S, K, startDate, expDate, sigma, R, cpnLow, cpnHigh, Q=0.0):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv="ACT/365")
    # cpnLow는 기초자산이 행사가 밑일때 지급하는 쿠폰
    # cpnHigh는 기초자산이 행사가 위일때 지급하는 쿠폰
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    if T == 0:
        return cpnHigh if S > K else cpnLow
    d2 = (log(S / K) + (R - Q - 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return exp(-R * T) * (cpnHigh * CND(d2) + cpnLow * CND(-d2))
