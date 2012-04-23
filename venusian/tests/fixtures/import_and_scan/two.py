from .decorators import decotwo

@decotwo(function=True)
def twofunction(request): # pragma: no cover
    return request
