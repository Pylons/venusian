import sys

PY3 = sys.version_info[0] == 3

try: # pragma: no cover
    from pkgutil import walk_packages
except ImportError: # pragma: no cover
    from pkgutil_26 import walk_packages

if PY3: # pragma: no cover
    def is_nonstr_iter(v):
        if isinstance(v, str):
            return False
        return hasattr(v, '__iter__')
else:
    def is_nonstr_iter(v):
        return hasattr(v, '__iter__')
    
