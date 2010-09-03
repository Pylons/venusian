from venusian.tests.fixtures.one import categorydecorator
from venusian.tests.fixtures.one import categorydecorator2

@categorydecorator(function=True)
def function(request): # pragma: no cover
    return request

@categorydecorator2(function=True)
def function2(request): # pragma: no cover
    return request
