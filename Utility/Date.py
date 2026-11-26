from holidays import financial_holidays
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import lru_cache

"""
한국거래소 KRX: XKRX
상하이거래소 SSE: XSHG
홍콩거래소 HKEX: XHKG
뉴욕거래소 NYSE: XNYS
일본거래소 JPX: XJPX
런던거래소 LSE: XLON
프랑크푸르트거래소 FWB: XETR
"""


def ConvDate(dateParam):
    # 날짜로 변환
    if isinstance(dateParam, datetime):
        return dateParam.date()
    if isinstance(dateParam, date):
        return dateParam
    if type(dateParam) == int:
        dateParam = str(dateParam)
    if len(dateParam) == 10 and dateParam[4] == "-" and dateParam[7] == "-":
        convertedDate = date(
            int(dateParam[0:4]), int(dateParam[5:7]), int(dateParam[8:10])
        )
    else:
        convertedDate = date(
            int(dateParam[0:4]), int(dateParam[4:6]), int(dateParam[6:8])
        )
    return convertedDate


@lru_cache  # 동일 인풋 조합이면 기존 임시저장된 값을 반환하며 계산량 줄임
def LoadHoliday(exchange, year):
    return frozenset(financial_holidays(market=exchange, years=year).keys())


def IsHoliday(dateParam, exchange="XKRX"):
    exchange = exchange.upper()
    convDate = ConvDate(dateParam)
    weekday = convDate.isoweekday()
    exchangeHoliday = LoadHoliday(exchange=exchange, year=convDate.year)
    if weekday > 5 or convDate in exchangeHoliday:
        return True
    else:
        return False


def AdjustHoliday(dateParam, exchange="XKRX", convention="MF"):
    convention = convention.upper()
    if convention not in ("F", "MF", "P"):
        raise ValueError("Incorrect Convention")
    convDate = ConvDate(dateParam)

    if convention == "F":
        while IsHoliday(convDate, exchange=exchange):
            convDate += timedelta(days=1)
        return convDate
    elif convention == "MF":
        while IsHoliday(convDate, exchange=exchange):
            prevDate = convDate
            convDate += timedelta(days=1)
            if prevDate.month != convDate.month:
                while IsHoliday(prevDate, exchange=exchange):
                    prevDate -= timedelta(days=1)
                return prevDate
        return convDate
    elif convention == "P":
        while IsHoliday(convDate, exchange=exchange):
            convDate -= timedelta(days=1)
        return convDate


def Time2Mat(startDate, endDate, conv="ACT/ACT"):
    # 30/360은 별도의 공식이 존재(2006 ISDA Definition 4.16(f)) 추가 필요
    # ACT/365F 추가 필요
    conv = str(conv).upper()
    if type(conv) == int:
        conv = str(conv)
    if conv not in ("ACT/ACT", "ACT/365", "ACT/360"):
        raise ValueError(
            "Incorrect Convention. Available ['ACT/ACT', 'ACT/365', 'ACT/360]'"
        )

    startDate = ConvDate(startDate)
    endDate = ConvDate(endDate)

    if conv == "ACT/365":
        return (endDate - startDate).days / 365
    elif conv == "ACT/360":
        return (endDate - startDate).days / 360
    elif conv == "ACT/ACT":
        if endDate.year == startDate.year:
            return (endDate - startDate).days / (
                date(endDate.year + 1, 1, 1) - date(startDate.year, 1, 1)
            ).days
        else:
            yearDiff = endDate.year - startDate.year - 1
            endPeriod = (endDate - date(endDate.year, 1, 1)).days / (
                date(endDate.year + 1, 1, 1) - date(endDate.year, 1, 1)
            ).days
            startPeriod = (date(startDate.year + 1, 1, 1) - startDate).days / (
                date(startDate.year + 1, 1, 1) - date(startDate.year, 1, 1)
            ).days
            totalPeriod = startPeriod + yearDiff + endPeriod
            return totalPeriod


def MakeSchedule(
    startDate, endDate, yearlyCpnNums, stub="L", exchange="XKRX", convention="MF"
):
    # 현금흐름 날짜 생성
    # 만기일로부터 역산하여 쿠폰 스케쥴 날짜 생성하는 것이 핵심
    # 쿠폰 계산일(달력일)과 지급일(영업일)의 괴리가 가능하기에 두개의 날짜 리스트로 반환
    stub = stub.upper()
    convStart = ConvDate(startDate)
    convEnd = ConvDate(endDate)

    if convStart >= convEnd:
        raise ValueError("Incorrect Start Date and End Date")

    if yearlyCpnNums not in [1, 2, 4, 6, 12]:
        raise ValueError("Incorrect Coupon Numbers")
    scheduleList = []
    i = 1
    scheduleList.append(convEnd)
    while scheduleList[-1] > convStart:
        scheduleList.append(
            scheduleList[0] - relativedelta(months=int(12 / yearlyCpnNums * i))
        )
        i += 1

    scheduleList.sort()

    if scheduleList[0] != convStart:
        scheduleList[0] = convStart
        if stub == "L":
            if scheduleList[1] != convEnd:
                scheduleList.pop(1)
    adjustedSchedule = []
    for j in range(len(scheduleList)):
        adjustedSchedule.append(
            AdjustHoliday(scheduleList[j], exchange=exchange, convention=convention)
        )
    adjustedSchedule[0] = scheduleList[0]

    return scheduleList, adjustedSchedule


def AddBizDay(dateParam, offset, exchange="XKRX", convention="MF"):
    convDate = ConvDate(dateParam)
    bizDayCount = 0
    if offset == 0:
        convDate = AdjustHoliday(convDate, exchange=exchange, convention=convention)
        return convDate
    else:
        while bizDayCount != abs(offset):
            if offset > 0:
                convDate += timedelta(days=1)
            elif offset < 0:
                convDate -= timedelta(days=1)
            if not IsHoliday(convDate, exchange=exchange):
                bizDayCount += 1
        return convDate


if __name__ == "__main__":
    # 테스트
    print(MakeSchedule("20260328", "20270330", 1))
