class _Call(tuple):  # pragma: no cover
    def __new__(cls, value=(), name=None):
        name = ''
        args = ()
        kwargs = {}
        _len = len(value)
        if _len == 3:
            name, args, kwargs = value
        return tuple.__new__(cls, (name, args, kwargs))

    def __init__(self, value=(), name=None):
        self.name = name

    def __call__(self, *args, **kwargs):
        if self.name is None:
            return _Call(('', args, kwargs), name='()')
        else:
            return _Call((self.name, args, kwargs), name=self.name + '()')

    def __getattr__(self, attr):
        if self.name is None:
            return _Call(name=attr)
        else:
            return _Call(name='%s.%s' % (self.name, attr))


call = _Call()
