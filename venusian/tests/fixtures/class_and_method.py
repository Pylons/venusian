from venusian.tests.fixtures import decorator


@decorator(class_=True)
class Class(object):

    @decorator(method=True)
    def method(self):
        pass
