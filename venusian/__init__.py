import imp
import inspect
import sys

from venusian.compat import walk_packages
from venusian.advice import getFrameInfo

ATTACH_ATTR = '__venusian_callbacks__'

class Scanner(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def scan(self, package, categories=None, onerror=None):
        """ Scan a Python package and any of its subpackages.  All
        top-level objects will be considered; those marked with
        venusian callback attributes related to ``category`` will be
        processed.

        The ``package`` argument should be a reference to a Python
        package or module object.

        The ``categories`` argument should be sequence of Venusian
        callback categories (each category usually a string) or the
        special value ``None`` which means all Venusian callback
        categories.  The default is ``None``.

        The ``onerror`` argument should either be ``None`` or a callback
        function which behaves the same way as the ``onerror`` callback
        function described in
        http://docs.python.org/library/pkgutil.html#pkgutil.walk_packages .

        By default, during a scan, Venusian will propagate all errors that
        happen during its code importing process, including
        :exc:`ImportError`.  If you use a custom ``onerror`` callback, you
        can change this behavior.
        
        Here's an example ``onerror`` callback that ignores
        :exc:`ImportError`::

            import sys
            def onerror(name):
                if not issubclass(sys.exc_info()[0], ImportError):
                    raise # reraise the last exception

        The ``name`` passed to ``onerror`` is the module or package dotted
        name that could not be imported due to an exception.

        .. note:: the ``onerror`` callback is new as of Venusian 1.0.
        """
        if onerror is None:
            # by default, propagate all errors (for bw compat purposes)
            def onerror(name):
                raise

        seen = set()
        def invoke(name, ob):
            # in one scan, we only process each object once
            if id(ob) in seen:
                return
            seen.add(id(ob))
            
            category_keys = categories
            try:
                # Some metaclasses do insane things when asked for an
                # ``ATTACH_ATTR``, like not raising an AttributeError but
                # some other arbitary exception.  Some even shittier
                # introspected code lets us access ``ATTACH_ATTR`` far but
                # barfs on a second attribute access for ``attached_to``
                # (still not raising an AttributeError, but some other
                # arbitrary exception).  Finally, the shittiest code of all
                # allows the attribute access of the ``ATTACH_ATTR`` *and*
                # ``attached_to``, (say, both ``ob.__getattr__`` and
                # ``attached_categories.__getattr__`` returning a proxy for
                # any attribute access), which either a) isn't callable or b)
                # is callable, but, when called, shits its pants in an
                # potentially arbitrary way (although for b, only TypeError
                # has been seen in the wild, from PyMongo).  Thus the
                # catchall except: return here, which in any other case would
                # be high treason.
                attached_categories = getattr(ob, ATTACH_ATTR)
                if not attached_categories.attached_to(ob):
                    return
            except:
                return
            if category_keys is None:
                category_keys = list(attached_categories.keys())
                category_keys.sort()
            for category in category_keys:
                callbacks = attached_categories.get(category, [])
                for callback in callbacks:
                    callback(self, name, ob)

        for name, ob in inspect.getmembers(package):
            invoke(name, ob)

        if hasattr(package, '__path__'): # package, not module
            results = walk_packages(package.__path__, package.__name__+'.',
                                    onerror=onerror)

            for importer, modname, ispkg in results:
                loader = importer.find_module(modname)
                if loader is not None: # happens on pypy with orphaned pyc
                    try:
                        module_type = loader.etc[2]
                        # only scrape members from non-orphaned source files
                        # and package directories
                        if module_type in (imp.PY_SOURCE, imp.PKG_DIRECTORY):
                            # NB: use __import__(modname) rather than
                            # loader.load_module(modname) to prevent
                            # inappropriate double-execution of module code
                            try:
                                __import__(modname)
                            except Exception:
                                onerror(modname)
                            module = sys.modules.get(modname)
                            if module is not None:
                                for name, ob in inspect.getmembers(module,
                                                                   None):
                                    invoke(name, ob)
                    finally:
                        if  ( hasattr(loader, 'file') and
                              hasattr(loader.file,'close') ):
                            loader.file.close()

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

    ``category``

      The ``category`` argument passed to ``attach`` (or ``None``, the
      default).

    ``codeinfo``

      A tuple in the form ``(filename, lineno, function, sourceline)``
      representing the context of the venusian decorator used.  Eg.
      ``('/home/chrism/projects/venusian/tests/test_advice.py', 81,
      'testCallInfo', 'add_handler(foo, bar)')``
      
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)

class Categories(dict):
    def __init__(self, attached_to):
        super(dict, self).__init__()
        if attached_to is None:
            self.attached_id = None
        else:
            self.attached_id = id(attached_to)

    def attached_to(self, obj):
        if self.attached_id:
            return self.attached_id == id(obj)
        return True
    
def attach(wrapped, callback, category=None, depth=1):
    """ Attach a callback to the wrapped object.  It will be found
    later during a scan.  This function returns an instance of the
    :class:`venusian.AttachInfo` class."""

    frame = sys._getframe(depth+1)
    scope, module, f_locals, f_globals, codeinfo = getFrameInfo(frame)
    if scope == 'class':
        # we're in the midst of a class statement
        categories = f_locals.setdefault(ATTACH_ATTR, Categories(None))
        callbacks = categories.setdefault(category, [])
        callbacks.append(callback)
    else:
        categories = getattr(wrapped, ATTACH_ATTR, None)
        if categories is None or not categories.attached_to(wrapped):
            # if there aren't any attached categories, or we've retrieved
            # some by inheritance, we need to create new ones
            categories = Categories(wrapped)
            setattr(wrapped, ATTACH_ATTR, categories)
        callbacks = categories.setdefault(category, [])
        callbacks.append(callback)
    return AttachInfo(
        scope=scope, module=module, locals=f_locals, globals=f_globals,
        category=category, codeinfo=codeinfo)
