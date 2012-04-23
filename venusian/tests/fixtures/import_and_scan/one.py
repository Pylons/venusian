from .decorators import decoone
from .two import twofunction # should not be scanned

@decoone(function=True)
def onefunction(request): # pragma: no cover
    twofunction(request)
    return request
