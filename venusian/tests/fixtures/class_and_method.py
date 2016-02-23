from venusian.tests.fixtures import decorator


@decorator(class_=True)
class ClassWithMethod(object):

    @decorator(method=True)
    def method_on_class(self): # pragma: no cover
        pass
