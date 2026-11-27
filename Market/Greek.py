from Utility.Math import CND, PDF, exp, log, sqrt


def BSDelta(S, K, T, sigma, R, Q=0.0, isCall=True):
    if sigma <= 0 or S <= 0 or T < 0:
        raise ValueError("Incorrect Input")

    if T == 0:
        if isCall:
            if S > K:
                return 1
            else:
                return 0
        else:
            if S < K:
                return -1
            else:
                return 0
    else:
        d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
        if isCall:
            return exp(-Q * T) * CND(d1)
        else:
            return exp(-Q * T) * (CND(d1) - 1)


def BSGamma(S, K, T, sigma, R, Q=0.0):
    if sigma <= 0 or S <= 0 or T <= 0:
        raise ValueError("Incorrect Input")

    d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return exp(-Q * T) * PDF(d1) / (S * sigma * sqrt(T))


def BSVega(S, K, T, sigma, R, Q=0.0):
    # 블랙숄즈 닫힌해 형식, 풋과 콜 동일
    # 내재변동성 역산시 뉴튼랩슨 알고리즘에 사용
    if sigma <= 0 or S <= 0 or T <= 0:
        raise ValueError("Incorrect Input")
    d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return S * exp(-Q * T) * sqrt(T) * PDF(d1)
