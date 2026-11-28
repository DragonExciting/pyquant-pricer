# 국고04250-3606(26-6) (KR103503GG60) | 국채전문유통
# 발행일 2026/06/10
# 만기일 2036/06/10
# 10년 지표물
# 표면금리 	4.250
# 20261127기준 YTM 3.835%, 종가 10,529, 시가평가가격 10,574.57

from ProductType.Bond import FixedBond

valDate = 20261127

issueDate = 20260610
matDate = 20360610
cpnNums = 2
cpnRate = 0.0425
ytm = 0.03835

if __name__ == "__main__":
    print(
        FixedBond(
            tenorArray=10,
            rateArray=ytm,
            issueDate=issueDate,
            endDate=matDate,
            valDate=valDate,
            cpnRate=cpnRate,
            yearlyCpnNums=cpnNums,
        )
    )
