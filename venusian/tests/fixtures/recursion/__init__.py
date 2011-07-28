from venusian.tests.fixtures import decorator

@decorator(function=True)
def package_function(request): # pragma: no cover
    return request
