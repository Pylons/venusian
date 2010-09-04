try: # pragma: no cover
    from pkgutil import walk_packages
except ImportError: # pragma: no cover
    from pkgutil_26 import walk_packages
