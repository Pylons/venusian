import venusian

class decorator(object):
    category = None
    call_count = {}
    def __call__(self, wrapped):
        info = venusian.attach(wrapped, self.callback, category=self.category)
        return wrapped

    def callback(self, context, name, ob):
        ob_id = id(self)

        # count the number of times this decorator's callback has been called
        class_call_count = self.call_count.get(name, 0)
        self.call_count[name] = class_call_count + 1

        # count the number of times any decorator for this class has been called
        decorator_call_count = self.call_count.get(ob_id, 0)
        self.call_count[ob_id] = decorator_call_count + 1




class SuperClass(object):
    @decorator()
    def decorated_method(self):
        pass

@decorator()
class DecoratedSubClass(SuperClass):
    pass

class UndecoratedSubClass(SuperClass):
    pass

@decorator()
class AnotherDecoratedSubClass(SuperClass):
    pass
