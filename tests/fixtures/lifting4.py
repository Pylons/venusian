from tests.fixtures import categorydecorator, categorydecorator2
from venusian import lift, onlyliftedfrom


@onlyliftedfrom()
class Super(object):  # pragma: no cover
    @categorydecorator()
    def hiss(self):
        pass

    @categorydecorator2()
    def jump(self):
        pass


@lift(("mycategory",))
class Sub(Super):  # pragma: no cover
    def hiss(self):
        pass

    def jump(self):
        pass

    @categorydecorator2()
    def smack(self):
        pass
