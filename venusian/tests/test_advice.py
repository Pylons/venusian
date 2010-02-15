##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for advice

This module was adapted from 'protocols.tests.advice', part of the Python
Enterprise Application Kit (PEAK).  Please notify the PEAK authors
(pje@telecommunity.com and tsarna@sarna.org) if bugs are found or
Zope-specific changes are required, so that the PEAK version of this module
can be kept in sync.

PEAK is a Python application framework that interoperates with (but does
not require) Zope 3 and Twisted.  It provides tools for manipulating UML
models, object-relational persistence, aspect-oriented programming, and more.
Visit the PEAK home page at http://peak.telecommunity.com for more information.

$Id: test_advice.py 40836 2005-12-16 22:40:51Z benji_york $
"""

import unittest
from types import ClassType
import sys
from venusian import advice

def ping(log, value):

    def pong(klass):
        log.append((value,klass))
        return [klass]

    advice.addClassAdvisor(pong)

class ClassicClass:
    __metaclass__ = ClassType
    classLevelFrameInfo = advice.getFrameInfo(sys._getframe())

class NewStyleClass:
    __metaclass__ = type
    classLevelFrameInfo = advice.getFrameInfo(sys._getframe())

moduleLevelFrameInfo = advice.getFrameInfo(sys._getframe())

class FrameInfoTest(unittest.TestCase):

    classLevelFrameInfo = advice.getFrameInfo(sys._getframe())

    def testModuleInfo(self):
        kind, module, f_locals, f_globals = moduleLevelFrameInfo
        self.assertEquals(kind, "module")
        for d in module.__dict__, f_locals, f_globals:
            self.assert_(d is globals())

    def testClassicClassInfo(self):
        kind, module, f_locals, f_globals = ClassicClass.classLevelFrameInfo
        self.assertEquals(kind, "class")

        self.assert_(f_locals is ClassicClass.__dict__)  # ???
        for d in module.__dict__, f_globals:
            self.assert_(d is globals())

    def testNewStyleClassInfo(self):
        kind, module, f_locals, f_globals = NewStyleClass.classLevelFrameInfo
        self.assertEquals(kind, "class")

        for d in module.__dict__, f_globals:
            self.assert_(d is globals())

    def testCallInfo(self):
        kind, module, f_locals, f_globals = advice.getFrameInfo(sys._getframe())
        self.assertEquals(kind, "function call")
        self.assert_(f_locals is locals()) # ???
        for d in module.__dict__, f_globals:
            self.assert_(d is globals())


class AdviceTests(unittest.TestCase):

    def testOrder(self):
        log = []
        class Foo(object):
            ping(log, 1)
            ping(log, 2)
            ping(log, 3)

        # Strip the list nesting
        for i in 1,2,3:
            self.assert_(isinstance(Foo, list))
            Foo, = Foo

        self.assertEquals(log, [(1, Foo), (2, [Foo]), (3, [[Foo]])])

    def testDoubleType(self): # pragma: no cover
        if sys.hexversion >= 0x02030000:
            return  # you can't duplicate bases in 2.3
        class aType(type,type):
            ping([],1)
        aType, = aType
        self.assert_(aType.__class__ is type)

    def testSingleExplicitMeta(self):

        class M(type):
            pass

        class C(M):
            __metaclass__ = M
            ping([],1)

        C, = C
        self.assert_(C.__class__ is M)


    def testMixedMetas(self):

        class M1(type): pass
        class M2(type): pass

        class B1: __metaclass__ = M1
        class B2: __metaclass__ = M2

        try:
            class C(B1,B2):
                ping([],1)
        except TypeError:
            pass
        else: # pragma: no cover
            raise AssertionError("Should have gotten incompatibility error")

        class M3(M1,M2): pass

        class C(B1,B2):
            __metaclass__ = M3
            ping([],1)

        self.assert_(isinstance(C,list))
        C, = C
        self.assert_(isinstance(C,M3))

    def testMetaOfClass(self):

        class metameta(type):
            pass

        class meta(type):
            __metaclass__ = metameta

        self.assertEquals(advice.determineMetaclass((meta, type)), metameta)

