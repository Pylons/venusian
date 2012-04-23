from venusian.tests.fixtures import decorator
from .two import twofunction # should not be scanned

@decorator(function=True)
def onefunction(request): # pragma: no cover
    twofunction(request)
    return request
