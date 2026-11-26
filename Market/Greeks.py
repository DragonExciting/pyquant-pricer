from Utility.Math import exp, sqrt, PDF, log


def Vega(S, K, T, sigma, R, Q=0.0):
    # 블랙숄즈 닫힌해 형식
    # 내재변동성 역산시 뉴튼랩슨 알고리즘에 사용
    d1 = (log(S / K) + (R - Q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return S * exp(-Q * T) * sqrt(T) * PDF(d1)
