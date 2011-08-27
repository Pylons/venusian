import unittest
import sys


class Test(object):
    def __init__(self):
        self.registrations = []
    def __call__(self, **kw):
        self.registrations.append(kw)

class TestScanner(unittest.TestCase):
    def _makeOne(self, **kw):
        from venusian import Scanner
        return Scanner(**kw)

    def test_package(self):
        from venusian.tests.fixtures import one
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(one)
        self.assertEqual(len(test.registrations), 6)
        test.registrations.sort(key=lambda x: (x['name'], x['ob'].__module__))
        from venusian.tests.fixtures.one.module import function as func1
        from venusian.tests.fixtures.one.module2 import function as func2
        from venusian.tests.fixtures.one.module import inst as inst1
        from venusian.tests.fixtures.one.module2 import inst as inst2
        from venusian.tests.fixtures.one.module import Class as Class1
        from venusian.tests.fixtures.one.module2 import Class as Class2

        self.assertEqual(test.registrations[0]['name'], 'Class')
        self.assertEqual(test.registrations[0]['ob'], Class1)
        self.assertEqual(test.registrations[0]['method'], True)

        self.assertEqual(test.registrations[1]['name'], 'Class')
        self.assertEqual(test.registrations[1]['ob'], Class2)
        self.assertEqual(test.registrations[1]['method'], True)

        self.assertEqual(test.registrations[2]['name'], 'function')
        self.assertEqual(test.registrations[2]['ob'], func1)
        self.assertEqual(test.registrations[2]['function'], True)

        self.assertEqual(test.registrations[3]['name'], 'function')
        self.assertEqual(test.registrations[3]['ob'], func2)
        self.assertEqual(test.registrations[3]['function'], True)
        
        self.assertEqual(test.registrations[4]['name'], 'inst')
        self.assertEqual(test.registrations[4]['ob'], inst1)
        self.assertEqual(test.registrations[4]['instance'], True)

        self.assertEqual(test.registrations[5]['name'], 'inst')
        self.assertEqual(test.registrations[5]['ob'], inst2)
        self.assertEqual(test.registrations[5]['instance'], True)

    def test_package_with_orphaned_pyc_file(self):
        # There is a module2.pyc file in the "pycfixtures" package; it
        # has no corresponding .py source file.  Such orphaned .pyc
        # files should be ignored during scanning.
        from venusian.tests.fixtures import pyc
        test = Test()
        scanner = self._makeOne(test=test) 
        scanner.scan(pyc)
        self.assertEqual(len(test.registrations), 4)
        test.registrations.sort(key=lambda x: (x['name'], x['ob'].__module__))
        from venusian.tests.fixtures.pyc.module import function as func1
        from venusian.tests.fixtures.pyc.module import inst as inst1
        from venusian.tests.fixtures.pyc.module import Class as Class1
        from venusian.tests.fixtures.pyc import subpackage

        self.assertEqual(test.registrations[0]['name'], 'Class')
        self.assertEqual(test.registrations[0]['ob'], Class1)
        self.assertEqual(test.registrations[0]['method'], True)

        self.assertEqual(test.registrations[1]['name'], 'function')
        self.assertEqual(test.registrations[1]['ob'], func1)
        self.assertEqual(test.registrations[1]['function'], True)

        self.assertEqual(test.registrations[2]['name'], 'inst')
        self.assertEqual(test.registrations[2]['ob'], inst1)
        self.assertEqual(test.registrations[2]['instance'], True)

        self.assertEqual(test.registrations[3]['name'], 'pkgfunction')
        self.assertEqual(test.registrations[3]['ob'], subpackage.pkgfunction)
        self.assertEqual(test.registrations[3]['function'], True)

    def test_module(self):
        from venusian.tests.fixtures.one import module
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(module)
        self.assertEqual(len(test.registrations), 3)
        test.registrations.sort(key=lambda x: (x['name'], x['ob'].__module__))
        from venusian.tests.fixtures.one.module import function as func1
        from venusian.tests.fixtures.one.module import inst as inst1
        from venusian.tests.fixtures.one.module import Class as Class1

        self.assertEqual(test.registrations[0]['name'], 'Class')
        self.assertEqual(test.registrations[0]['ob'], Class1)
        self.assertEqual(test.registrations[0]['method'], True)

        self.assertEqual(test.registrations[1]['name'], 'function')
        self.assertEqual(test.registrations[1]['ob'], func1)
        self.assertEqual(test.registrations[1]['function'], True)

        self.assertEqual(test.registrations[2]['name'], 'inst')
        self.assertEqual(test.registrations[2]['ob'], inst1)
        self.assertEqual(test.registrations[2]['instance'], True)

    def test_one_category(self):
        from venusian.tests.fixtures import category
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(category, categories=('mycategory',))
        self.assertEqual(len(test.registrations), 1)
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], category.function)
        self.assertEqual(test.registrations[0]['function'], True)

    def test_all_categories_implicit(self):
        from venusian.tests.fixtures import category
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(category)
        self.assertEqual(len(test.registrations), 2)
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], category.function)
        self.assertEqual(test.registrations[0]['function'], True)
        self.assertEqual(test.registrations[1]['name'], 'function2')
        self.assertEqual(test.registrations[1]['ob'], category.function2)
        self.assertEqual(test.registrations[1]['function'], True)

    def test_all_categories_explicit(self):
        from venusian.tests.fixtures import category
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(category, categories=('mycategory', 'mycategory2'))
        self.assertEqual(len(test.registrations), 2)
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], category.function)
        self.assertEqual(test.registrations[0]['function'], True)
        self.assertEqual(test.registrations[1]['name'], 'function2')
        self.assertEqual(test.registrations[1]['ob'], category.function2)
        self.assertEqual(test.registrations[1]['function'], True)

    if sys.version_info >= (2, 6):

        def test_decorations_arent_inherited(self):
            from venusian.tests.fixtures import inheritance
            test = Test()
            scanner = self._makeOne(test=test)
            scanner.scan(inheritance)
            self.assertEqual(test.registrations, [
                dict(name='Parent',
                     ob=inheritance.Parent),
                ])

        def test_classdecorator(self): # pragma: no cover
            from venusian.tests.fixtures import classdecorator
            test = Test()
            scanner = self._makeOne(test=test)
            scanner.scan(classdecorator)
            test.registrations.sort(key=lambda x: (x['name'], x['ob'].__module__))
            self.assertEqual(len(test.registrations), 2)
            self.assertEqual(test.registrations[0]['name'], 'SubClass')
            self.assertEqual(test.registrations[0]['ob'],
                             classdecorator.SubClass)
            self.assertEqual(test.registrations[0]['subclass'], True)
            self.assertEqual(test.registrations[1]['name'], 'SuperClass')
            self.assertEqual(test.registrations[1]['ob'],
                             classdecorator.SuperClass)
            self.assertEqual(test.registrations[1]['superclass'], True)

        def test_scan_only_finds_classdecoration_once(self):
            from venusian.tests.fixtures import two
            from venusian.tests.fixtures.two.mod1 import Class
            test = Test()
            scanner = self._makeOne(test=test)
            scanner.scan(two)
            self.assertEqual(test.registrations, [
                dict(name='Class',
                     ob=Class),
                ])
            
    def test_importerror_during_scan_default_onerror(self):
        from venusian.tests.fixtures import importerror
        test = Test()
        scanner = self._makeOne(test=test)
        # without a custom onerror, scan will propagate the importerror from
        # will_raise_importerror
        self.assertRaises(ImportError, scanner.scan, importerror)

    def test_importerror_during_scan_custom_onerror(self):
        from venusian.tests.fixtures import importerror
        test = Test()
        scanner = self._makeOne(test=test)
        # with this custom onerror, scan will not propagate the importerror
        # from will_raise_importerror
        def onerror(name):
            if not issubclass(sys.exc_info()[0], ImportError): raise
        scanner.scan(importerror, onerror=onerror)
        self.assertEqual(len(test.registrations), 1)
        from venusian.tests.fixtures.importerror import function as func1
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], func1)
        self.assertEqual(test.registrations[0]['function'], True)

    def test_attrerror_during_scan_custom_onerror(self):
        from venusian.tests.fixtures import attrerror
        test = Test()
        scanner = self._makeOne(test=test)
        # with this custom onerror, scan will not propagate the importerror
        # from will_raise_importerror
        def onerror(name):
            if not issubclass(sys.exc_info()[0], ImportError): raise
        self.assertRaises(AttributeError, scanner.scan, attrerror,
                          onerror=onerror)
        self.assertEqual(len(test.registrations), 1)
        from venusian.tests.fixtures.attrerror import function as func1
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], func1)
        self.assertEqual(test.registrations[0]['function'], True)

    def test_onerror_used_to_swallow_all_exceptions(self):
        from venusian.tests.fixtures import subpackages
        test = Test()
        scanner = self._makeOne(test=test)
        # onerror can also be used to skip errors while scanning submodules
        # e.g.: test modules under a given library
        swallowed = []
        def ignore_child(name):
            swallowed.append(name)
        scanner.scan(subpackages, onerror=ignore_child)
        self.assertEqual(swallowed,
          ['venusian.tests.fixtures.subpackages.childpackage.will_cause_import_error',
           'venusian.tests.fixtures.subpackages.mod2'])
        self.assertEqual(len(test.registrations), 1)
        from venusian.tests.fixtures.subpackages import function as func1
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], func1)
        self.assertEqual(test.registrations[0]['function'], True)
