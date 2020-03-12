import unittest

from expy.expression import *


class TestExpression(unittest.TestCase):

    def test_abstract_expression(self):
        @abstract_expression
        class Abstract(Expression): pass
        class Concrete(Abstract): pass
        self.assertRaises(TypeError, Abstract)
        Concrete()

    def test_field_inheritence(self):
        class A(Expression):
            parent = Field(int)
        class B(A):
            child1 = Field(int)
            child2 = Field(int)
        self.assertTupleEqual(A._fields, (A.parent,))
        self.assertTupleEqual(B._fields, (A.parent, B.child1, B.child2))

    def test_set_membership(self):
        class A(Expression):
            value = Field(int)
        class B(Expression):
            value = Field(int)
        test_set = set([A(0)])
        self.assertIn(A(0), test_set)
        self.assertNotIn(A(1), test_set)
        self.assertNotIn(B(0), test_set)
