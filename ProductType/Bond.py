from Market.Curve import LoadDF
from Utility.Date import ConvDate, MakeSchedule, Time2Mat


def FixedBond(
    tenorArray,
    rateArray,
    valDate,
    issueDate,
    endDate,
    yearlyCpnNums,
    cpnRate,
    stub="L",
    exchange="XKRX",
    convention="MF",
    conv="ACT/ACT",
    par=10_000,
    dfType="DIS",
):
    valDate = ConvDate(valDate)
    endDate = ConvDate(endDate)
    if valDate > endDate:
        raise ValueError("This Bond is expired")
    cpnAmt = par * cpnRate / yearlyCpnNums

    _, payDates = MakeSchedule(
        startDate=issueDate,
        endDate=endDate,
        yearlyCpnNums=yearlyCpnNums,
        stub=stub,
        exchange=exchange,
        convention=convention,
    )

    a = []
    cpnPV = []
    i = 0
    for d in payDates[1:]:
        if d >= valDate:
            a.append(Time2Mat(startDate=valDate, endDate=d, conv=conv))
            cpnPV.append(
                LoadDF(tenorArray, rateArray, a[i], dfType=dfType, freq=yearlyCpnNums)
                * cpnAmt
            )
            i += 1
    # 짧은 구간에 대해 실제 일수로 일할 계산한 쿠폰이 붙도록 로직 변경 필요
    cpnPV[-1] = LoadDF(
        tenorArray, rateArray, a[-1], dfType=dfType, freq=yearlyCpnNums
    ) * (cpnAmt + par)
    bondValue = sum(cpnPV)
    return bondValue
