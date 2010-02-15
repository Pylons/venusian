import venusian

class decorator(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __call__(self, wrapped):
        view_config = self.__dict__.copy()
        def callback(context, name, ob):
            context.test(ob=ob, name=name, **view_config)
        info = venusian.attach(wrapped, callback)
        if info.scope == 'class':
            # we're in the midst of a class statement
            if view_config.get('attr') is None:
                view_config['attr'] = wrapped.__name__
        return wrapped
