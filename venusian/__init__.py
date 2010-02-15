import inspect
import sys

from venusian.compat import walk_packages
from venusian.advice import getFrameInfo

ATTACH_ATTR = '__venusian_callbacks__'

class Scanner(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def scan(self, package):
        """ Scan a Python package and any of its subpackages.  All
        top-level objects will be considered; those marked with
        venusian callback attributes will be processed.

        The ``package`` argument should be a reference to a Python
        package or module object.
        """
        def invoke(name, ob):
            callbacks = getattr(ob, ATTACH_ATTR, None)
            if callbacks is not None:
                for callback in callbacks:
                    callback(self, name, ob)

        for name, ob in inspect.getmembers(package):
            invoke(name, ob)

        if hasattr(package, '__path__'): # package, not module
            results = walk_packages(package.__path__, package.__name__+'.')

            for importer, modname, ispkg in results:
                __import__(modname)
                module = sys.modules[modname]
                for name, ob in inspect.getmembers(module, None):
                    invoke(name, ob)

class AttachInfo(object):
    """
    An instance of this class is returned by the
    :func:`venusian.attach` function.  It has the following
    attributes:

    ``scope``

      One of ``exec``, ``module``, ``class``, ``function call`` or
      ``unknown`` (each a string).  This is the scope detected while
      executing the decorator which runs the attach function.

    ``module``

      The module in which the decorated function was defined.

    ``locals``

      A dictionary containing decorator frame's f_locals.

    ``globals``

      A dictionary containing decorator frame's f_globals.
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)

def attach(wrapped, callback, depth=1):

    """ Attach a callback to the wrapped object.  It will be found
    later during a scan.  This function returns an instance of the
    :class:`venusian.AttachInfo` class."""

    frame = sys._getframe(depth+1)
    scope, module, f_locals, f_globals = getFrameInfo(frame)
    if scope == 'class':
        # we're in the midst of a class statement
        callbacks = f_locals.setdefault(ATTACH_ATTR, [])
        callbacks.append(callback)
    else:
        callbacks = getattr(wrapped, ATTACH_ATTR, [])
        callbacks.append(callback)
        setattr(wrapped, ATTACH_ATTR, callbacks)
    return AttachInfo(
        scope=scope, module=module, locals=f_locals, globals=f_globals)

    
    
