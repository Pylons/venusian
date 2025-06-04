import venusian


def decorator(wrapped):
    def callback(context, name, ob):
        raise ValueError

    venusian.attach(wrapped, callback)
    return wrapped


@decorator
def function(request):  # pragma: no cover
    return request
