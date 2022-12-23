import sys

if sys.version_info[0] == 3 and sys.version_info[1] < 10:

    def compat_find_loader(importer, modname):
        return importer.find_module(modname)

else:

    def compat_find_loader(importer, modname):
        spec = importer.find_spec(modname)
        return spec.loader
