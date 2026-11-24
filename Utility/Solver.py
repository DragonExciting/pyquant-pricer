"""
해찾기 -> 뉴튼-랩슨, 이분법
https://en.wikipedia.org/wiki/Newton%27s_method 참고
https://en.wikipedia.org/wiki/Bisection_method 참고
"""


def Newton(rootFunc, rootParam, target, tol=1e-8, maxTry=100):
    # 내재변동성: rootFunc = 블랙숄즈방정식, rootParam = 변동성, target = 옵션 시장가격
    # rootParam는 최초 해찾기 시행 값으로 상품군별로 찾는 값이 다르므로 지정필요

    diff = rootFunc(rootParam) - target
    eps = 6e-6 * max(abs(rootParam), 1.0)
    # 초기값에 따라 동적으로 epsilon 조절
    # 편미분 함수를 중앙차분으로 근사하기때문에 오차 최소화시키는 6e-6 이용
    # Numerical Optimization (Nocedal & Wright)
    i = 0
    while abs(diff) > tol and i < maxTry:
        diffFunc = (rootFunc(rootParam + eps) - rootFunc(rootParam - eps)) / (2 * eps)
        if abs(diffFunc) < 1e-6:
            raise ValueError("Differential Function is close to 0")
        rootParam = rootParam - diff / diffFunc
        eps = 6e-6 * max(abs(rootParam), 1.0)
        diff = rootFunc(rootParam) - target
        i += 1
    if abs(diff) > 1e-6:
        raise ValueError("Fail to find Root")
    return rootParam


def Bisection(rootFunc, rootParam, target, tol=1e-8, maxTry=100):
    return
