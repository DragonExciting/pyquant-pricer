from numpy import asarray, where
from Utility.Math import exp


def LoadDF(tenorArray, rateArray, targetTau):
    # Dataframe은 너무 느리기에 Numpy array 사용
    # 호출되는 array가 이미 오름차순으로 정리된 상태를 가정
    if targetTau < 0:
        raise ValueError("Target Tau must be non-negative")
    if len(tenorArray) != len(rateArray):
        raise ValueError("Tenor and Rate must be same length")
    if targetTau <= tenorArray[0]:
        return exp(-rateArray[0] * targetTau)
    elif targetTau >= tenorArray[-1]:
        return exp(-rateArray[-1] * targetTau)
    tenorArray = asarray(tenorArray, float)
    rateArray = asarray(rateArray, float)

    lowerIndex = where(targetTau >= tenorArray)[0][-1]
    lowerTenor = tenorArray[lowerIndex]
    higherIndex = where(targetTau <= tenorArray)[0][0]
    higherTenor = tenorArray[higherIndex]
    if lowerIndex == higherIndex:
        return exp(-rateArray[lowerIndex] * lowerTenor)
    targetRatio = (targetTau - lowerTenor) / (higherTenor - lowerTenor)

    lowerRate = rateArray[lowerIndex]
    higherRate = rateArray[higherIndex]
    return exp(-(lowerRate + (higherRate - lowerRate) * targetRatio) * targetTau)
