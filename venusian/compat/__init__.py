try:
    from pkgutil import walk_packages
except ImportError:
    from pkgutil_26 import walk_packages
