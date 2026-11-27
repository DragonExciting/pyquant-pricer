"""
해찾기 -> 뉴튼-랩슨, 이분법
https://en.wikipedia.org/wiki/Newton%27s_method 참고
https://en.wikipedia.org/wiki/Bisection_method 참고
"""


def Newton(rootFunc, rootParam, target, tol=1e-6, maxTry=100):
    # 내재변동성: rootFunc = 블랙숄즈방정식, rootParam = 변동성, target = 옵션 시장가격
    # rootParam는 최초 해찾기 시행 값으로 상품군별로 찾는 값이 다르므로 지정필요

    diff = rootFunc(rootParam) - target
    eps = 6e-6 * max(abs(rootParam), 1.0)
    # 초기값에 따라 동적으로 epsilon 조절
    # 편미분 함수를 중앙차분으로 근사하기때문에 오차 최소화시키는 값 이용
    # Numerical Optimization (Nocedal & Wright, 2006)
    i = 0
    while abs(diff) > tol and i < maxTry:
        diffFunc = (rootFunc(rootParam + eps) - rootFunc(rootParam - eps)) / (2 * eps)
        if abs(diffFunc) < tol:
            raise ValueError("Differential Function is close to 0")
        rootParam = rootParam - diff / diffFunc
        eps = 6e-6 * max(abs(rootParam), 1.0)
        diff = rootFunc(rootParam) - target
        i += 1
    if abs(diff) > tol:
        raise ValueError("Fail to find Root")
    return rootParam


def Bisection(rootFunc, target, low, high, tol=1e-6, maxTry=100):
    if low >= high:
        raise ValueError("Low must be lower than High")
    i = 0
    mid = low + (high - low) / 2
    while (high - low) / 2 > tol and i < maxTry:
        mid = low + (high - low) / 2
        diffLow = rootFunc(low) - target
        diffHigh = rootFunc(high) - target
        diffMid = rootFunc(mid) - target
        if (diffHigh > 0 and diffLow > 0) or (diffHigh < 0 and diffLow < 0):
            raise ValueError("Fail to find Root")
        elif diffMid == 0:
            return mid
        else:
            if (diffMid > 0) == (diffLow > 0):  # 왼쪽 끝과 같은 부호 -> 해는 오른쪽
                low = mid
            else:  # 다른 부호 -> 해는 왼쪽
                high = mid
        i += 1
    if abs((high - low) / 2) > tol:
        raise ValueError("Fail to find Root")
    return mid
