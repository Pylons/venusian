import imp
from inspect import getmembers
import sys

from venusian.compat import iter_modules
from venusian.compat import is_nonstr_iter
from venusian.advice import getFrameInfo

ATTACH_ATTR = '__venusian_callbacks__'

class Scanner(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def scan(self, package, categories=None, onerror=None, ignore=None):
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

        The ``ignore`` argument allows you to ignore certain modules,
        packages, or global objects during a scan.  It should be a sequence
        containing strings and/or callables that will be used to match
        against the full dotted name of each object encountered during a
        scan.  The sequence can contain any of these three types of objects:

        - A string representing a full dotted name.  To name an object by
          dotted name, use a string representing the full dotted name.  For
          example, if you want to ignore the ``my.package`` package *and any
          of its subobjects or subpackages* during the scan, pass
          ``ignore=['my.package']``.

        - A string representing a relative dotted name.  To name an object
          relative to the ``package`` passed to this method, use a string
          beginning with a dot.  For example, if the ``package`` you've
          passed is imported as ``my.package``, and you pass
          ``ignore=['.mymodule']``, the ``my.package.mymodule`` mymodule *and
          any of its subobjects or subpackages* will be omitted during scan
          processing.

        - A callable that accepts a full dotted name string of an object as
          its single positional argument and returns ``True`` or ``False``.
          For example, if you want to skip all packages, modules, and global
          objects with a full dotted path that ends with the word "tests", you
          can use ``ignore=[re.compile('tests$').search]``.  If the callable
          returns ``True`` (or anything else truthy), the object is ignored,
          if it returns ``False`` (or anything else falsy) the object is not
          ignored.  *Note that unlike string matches, ignores that use a
          callable don't cause submodules and subobjects of a module or
          package represented by a dotted name to also be ignored, they match
          individual objects found during a scan, including packages,
          modules, and global objects*.

        You can mix and match the three types of strings in the list.  For
        example, if the package being scanned is ``my``,
        ``ignore=['my.package', '.someothermodule',
        re.compile('tests$').search]`` would cause ``my.package`` (and all
        its submodules and subobjects) to be ignored, ``my.someothermodule``
        to be ignored, and any modules, packages, or global objects found
        during the scan that have a full dotted name that ends with the word
        ``tests`` to be ignored.

        Note that packages and modules matched by any ignore in the list will
        not be imported, and their top-level code will not be run as a result.

        A string or callable alone can also be passed as ``ignore`` without a
        surrounding list.
        
        .. note:: the ``ignore`` argument is new as of Venusian 1.1.
        """

        pkg_name = package.__name__

        if ignore is not None and not is_nonstr_iter(ignore):
            ignore = [ignore]
        
        def _ignore(fullname):
            if ignore is not None:
                for ign in ignore:
                    if isinstance(ign, str):
                        if ign.startswith('.'):
                            # leading dotted name relative to scanned package
                            if fullname.startswith(pkg_name + ign):
                                return True
                        else:
                            # non-leading-dotted name absolute object name
                            if fullname.startswith(ign):
                                return True
                    else:
                        # function
                        if ign(fullname):
                            return True
            return False

        seen = set()

        def invoke(mod_name, name, ob):
            # in one scan, we only process each object once
            if id(ob) in seen:
                return
            seen.add(id(ob))

            fullname = mod_name + '.' + name

            if _ignore(fullname):
                return

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

        for name, ob in getmembers(package):
            # whether it's a module or a package, we need to scan its
            # members; walk_packages only iterates over submodules and
            # subpackages
            invoke(pkg_name, name, ob)

        if hasattr(package, '__path__'): # package, not module
            results = walk_packages(package.__path__, package.__name__+'.',
                                    onerror=onerror, ignore=_ignore)

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
                                if onerror is not None:
                                    onerror(modname)
                                else:
                                    raise
                            module = sys.modules.get(modname)
                            if module is not None:
                                for name, ob in getmembers(module, None):
                                    invoke(modname, name, ob)
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

def walk_packages(path=None, prefix='', onerror=None, ignore=None):
    """Yields (module_loader, name, ispkg) for all modules recursively
    on path, or, if path is None, all accessible modules.

    'path' should be either None or a list of paths to look for
    modules in.

    'prefix' is a string to output on the front of every module name
    on output.

    Note that this function must import all *packages* (NOT all
    modules!) on the given path, in order to access the __path__
    attribute to find submodules.

    'onerror' is a function which gets called with one argument (the
    name of the package which was being imported) if any exception
    occurs while trying to import a package.  If no onerror function is
    supplied, ImportErrors are caught and ignored, while all other
    exceptions are propagated, terminating the search.

    'ignore' is a function fed a fullly dotted name; if it returns True, the
    object is skipped and not returned in results (and if it's a package it's
    not imported).

    Examples:

    # list all modules python can access
    walk_packages()

    # list all submodules of ctypes
    walk_packages(ctypes.__path__, ctypes.__name__+'.')

    # NB: we can't just use pkgutils.walk_packages because we need to ignore
    # things
    """

    def seen(p, m={}):
        if p in m: # pragma: no cover
            return True
        m[p] = True

    # iter_modules is nonrecursive
    for importer, name, ispkg in iter_modules(path, prefix):

        if ignore is not None and ignore(name):
            # if name is a package, ignoring here will cause
            # all subpackages and submodules to be ignored too
            continue

        # do any onerror handling before yielding

        if ispkg:
            try:
                __import__(name)
            except ImportError:
                if onerror is not None:
                    onerror(name)
            except Exception:
                if onerror is not None:
                    onerror(name)
                else:
                    raise
            else:
                yield importer, name, ispkg
                path = getattr(sys.modules[name], '__path__', None) or []

                # don't traverse path items we've seen before
                path = [p for p in path if not seen(p)]

                for item in walk_packages(path, name+'.', onerror):
                    yield item
        else:
            yield importer, name, ispkg
