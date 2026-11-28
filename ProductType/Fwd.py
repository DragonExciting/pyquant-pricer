from Utility.Date import Time2Mat
from Utility.Math import exp


# 만기 수개월 이내의 주식 선물과 주식 선도는 일일 정산의 효과를 미고려하더라도 차이가 미미함
# Options, Futures, and Other Derivatives, Ch.5.8 (Hull) 참고
def EquityFwd(S, startDate, expDate, R, Q=0.0, B=0.0, conv="ACT/365"):
    T = Time2Mat(startDate=startDate, endDate=expDate, conv=conv)
    if T is None:
        raise ValueError("Incorrect Input")
    if S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    # Q: 연속 배당 수익률 -> 이산배당을 할인하여 차감하는 기능 추가 필요
    # B: 대차 수수로율(Borrowing Cost)
    # Forward Price <> Forward Value 둘이 다름을 주의할 것
    # Forward Value라는 것은 최초 계약시점의 Forward Price대비 현재의 Forward Price 변동 손익
    return S * exp((R - Q - B) * T)
