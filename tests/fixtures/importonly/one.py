from tests.fixtures import decorator
from tests.fixtures.importonly.two import twofunction  # should not be scanned


@decorator(function=True)
def onefunction(request):  # pragma: no cover
    return request
