from numpy import asarray, atleast_1d, where

from Utility.Math import exp


# 파생상품과 채권의 할인 방식은 다름
def Rate2DF(rate, tau, dfType="CON", freq=2):
    dfType = dfType.upper()
    if dfType == "CON":
        return exp(-rate * tau)
    elif dfType == "DIS":
        return (1 + rate / freq) ** (-freq * tau)
    raise ValueError("Discount Factor type must be CON or DIS")


def LoadDF(tenorArray, rateArray, targetTau, dfType="CON", freq=2):
    tenorArray = atleast_1d(asarray(tenorArray, float))
    rateArray = atleast_1d(asarray(rateArray, float))
    dfType = dfType.upper()
    # Dataframe은 너무 느리기에 Numpy array 사용
    # 호출되는 array가 이미 오름차순으로 정리된 상태를 가정
    if targetTau < 0:
        raise ValueError("Target Tau must be non-negative")
    if len(tenorArray) != len(rateArray):
        raise ValueError("Tenor and Rate must be same length")
    if targetTau <= tenorArray[0]:
        return Rate2DF(rateArray[0], targetTau, dfType=dfType, freq=freq)
    elif targetTau >= tenorArray[-1]:
        return Rate2DF(rateArray[-1], targetTau, dfType=dfType, freq=freq)

    lowerIndex = where(targetTau >= tenorArray)[0][-1]
    # where: 해당 조건을 충족하는 인덱스들을 호출 -> 낮은 순번 인덱스부터 반환
    # tenorArray 중 targetTau 보다 낮은 것 중 가장 큰것은 맨 마지막 인덱스에 있음
    lowerTenor = tenorArray[lowerIndex]
    higherIndex = where(targetTau <= tenorArray)[0][0]
    higherTenor = tenorArray[higherIndex]
    if lowerIndex == higherIndex:
        return Rate2DF(rateArray[lowerIndex], lowerTenor, dfType=dfType, freq=freq)
    targetRatio = (targetTau - lowerTenor) / (higherTenor - lowerTenor)

    lowerRate = rateArray[lowerIndex]
    higherRate = rateArray[higherIndex]
    return Rate2DF(
        (lowerRate + (higherRate - lowerRate) * targetRatio),
        targetTau,
        dfType=dfType,
        freq=freq,
    )
