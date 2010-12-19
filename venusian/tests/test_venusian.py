import unittest
import sys

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
        test.registrations.sort(
            lambda x, y: cmp((x['name'], x['ob'].__module__),
                             (y['name'], y['ob'].__module__))
            )
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
        test.registrations.sort(
            lambda x, y: cmp((x['name'], x['ob'].__module__),
                             (y['name'], y['ob'].__module__))
            )
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
        test.registrations.sort(
            lambda x, y: cmp((x['name'], x['ob'].__module__),
                             (y['name'], y['ob'].__module__))
            )
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

        def test_classdecorator(self): # pragma: no cover
            from venusian.tests.fixtures import classdecorator
            test = Test()
            scanner = self._makeOne(test=test)
            scanner.scan(classdecorator)
            test.registrations.sort(
                lambda x, y: cmp((x['name'], x['ob'].__module__),
                                 (y['name'], y['ob'].__module__))
                )
            self.assertEqual(len(test.registrations), 2)
            self.assertEqual(test.registrations[0]['name'], 'SubClass')
            self.assertEqual(test.registrations[0]['ob'],
                             classdecorator.SubClass)
            self.assertEqual(test.registrations[0]['subclass'], True)
            self.assertEqual(test.registrations[1]['name'], 'SuperClass')
            self.assertEqual(test.registrations[1]['ob'],
                             classdecorator.SuperClass)
            self.assertEqual(test.registrations[1]['superclass'], True)

class Test(object):
    def __init__(self):
        self.registrations = []
    def __call__(self, **kw):
        self.registrations.append(kw)
