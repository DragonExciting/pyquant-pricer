from Utility.Math import exp


def EquityFwd(S, T, R, Q=0.0, B=0.0):
    if S <= 0 or T < 0:
        raise ValueError("Incorrect Input")
    # Q: 연속 배당 수익률 -> 이산배당을 할인하여 차감하는 기능 추가 필요
    # B: 대차 수수로율(Borrowing Cost)
    # Forward Price <> Forward Value 둘이 다름을 주의할 것
    # Forward Value라는 것은 최초 계약시점의 Forward Price대비 현재의 Forward Price 변동 손익
    return S * exp((R - Q - B) * T)
