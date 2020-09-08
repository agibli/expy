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
        class C(Expression):
            a = Field(A)
            b = Field(B)
        c = C(A(1), B(0))
        test_set = set([A(0), c])
        self.assertIn(A(0), test_set)
        self.assertIn(C(A(1), B(0)), test_set)
        self.assertIn(c, test_set)
        self.assertNotIn(A(1), test_set)
        self.assertNotIn(B(0), test_set)

    def test_outputs(self):
        class A(Expression): pass
        out1_ = Output(A)
        out2_ = Output(SelfType)
        class B(Expression):
            out1 = out1_
        class C(B):
            out2 = out2_
        b = B()
        c = C()
        self.assertIsInstance(b.out1, A)
        self.assertIsInstance(c.out1, A)
        self.assertIsInstance(c.out2, C)
        self.assertEqual(b.out1, B.out1(b))
        self.assertEqual(c.out1, C.out1(c))
        self.assertEqual(c.out2, C.out2(c))
        self.assertEqual(out1_.name, "out1")
        self.assertEqual(out2_.name, "out2")
        self.assertEqual(out1_.expression_type, B.out1)
        self.assertEqual(out1_.expression_type, C.out1)
        self.assertEqual(out2_.expression_type, C.out2)
        self.assertTupleEqual(B._outputs, (out1_,))
        self.assertTupleEqual(C._outputs, (out1_, out2_))


if __name__ == '__main__':
    unittest.main()
