import unittest

class TestScanner(unittest.TestCase):
    def _makeOne(self, **kw):
        from venusian import Scanner
        return Scanner(**kw)

    def test_package(self):
        from venusian.tests import fixtures
        class Test(object):
            def __init__(self):
                self.registrations = []
            def __call__(self, **kw):
                self.registrations.append(kw)
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(fixtures)
        self.assertEqual(len(test.registrations), 6)
        test.registrations.sort(
            lambda x, y: cmp((x['name'], x['ob'].__module__),
                             (y['name'], y['ob'].__module__))
            )
        from venusian.tests.fixtures.module import function as func1
        from venusian.tests.fixtures.module2 import function as func2
        from venusian.tests.fixtures.module import inst as inst1
        from venusian.tests.fixtures.module2 import inst as inst2
        from venusian.tests.fixtures.module import Class as Class1
        from venusian.tests.fixtures.module2 import Class as Class2

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

    def test_module(self):
        from venusian.tests.fixtures import module
        class Test(object):
            def __init__(self):
                self.registrations = []
            def __call__(self, **kw):
                self.registrations.append(kw)
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(module)
        self.assertEqual(len(test.registrations), 3)
        test.registrations.sort(
            lambda x, y: cmp((x['name'], x['ob'].__module__),
                             (y['name'], y['ob'].__module__))
            )
        from venusian.tests.fixtures.module import function as func1
        from venusian.tests.fixtures.module import inst as inst1
        from venusian.tests.fixtures.module import Class as Class1

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
        from venusian.tests import categoryfixture
        class Test(object):
            def __init__(self):
                self.registrations = []
            def __call__(self, **kw):
                self.registrations.append(kw)
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(categoryfixture, categories=('mycategory',))
        self.assertEqual(len(test.registrations), 1)
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], categoryfixture.function)
        self.assertEqual(test.registrations[0]['function'], True)

    def test_all_categories_implicit(self):
        from venusian.tests import categoryfixture
        class Test(object):
            def __init__(self):
                self.registrations = []
            def __call__(self, **kw):
                self.registrations.append(kw)
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(categoryfixture)
        self.assertEqual(len(test.registrations), 2)
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], categoryfixture.function)
        self.assertEqual(test.registrations[0]['function'], True)
        self.assertEqual(test.registrations[1]['name'], 'function2')
        self.assertEqual(test.registrations[1]['ob'], categoryfixture.function2)
        self.assertEqual(test.registrations[1]['function'], True)

    def test_all_categories_explicit(self):
        from venusian.tests import categoryfixture
        class Test(object):
            def __init__(self):
                self.registrations = []
            def __call__(self, **kw):
                self.registrations.append(kw)
        test = Test()
        scanner = self._makeOne(test=test)
        scanner.scan(categoryfixture, categories=('mycategory', 'mycategory2'))
        self.assertEqual(len(test.registrations), 2)
        self.assertEqual(test.registrations[0]['name'], 'function')
        self.assertEqual(test.registrations[0]['ob'], categoryfixture.function)
        self.assertEqual(test.registrations[0]['function'], True)
        self.assertEqual(test.registrations[1]['name'], 'function2')
        self.assertEqual(test.registrations[1]['ob'], categoryfixture.function2)
        self.assertEqual(test.registrations[1]['function'], True)
