import unittest

from expy.math_types import *
from expy.constant_folding import constant_folding


def _var_type(name, base):
    return type(base)(name, (base,), {"tag": Field(str)})

BooleanVar = _var_type("BooleanVar", Boolean)
IntegerVar = _var_type("IntegerVar", Integer)
ScalarVar = _var_type("ScalarVar", Scalar)
VectorVar = _var_type("VectorVar", Vector)


class TestConstantFolding(unittest.TestCase):

    def _assert_scalar_equal(self, const, value):
        self.assertIsInstance(const, ScalarConstant)
        self.assertAlmostEqual(const.value, value.value)

    def _assert_vector_equal(self, const, value):
        self.assertIsInstance(const, VectorConstant)
        self.assertAlmostEqual(const.xvalue, value.xvalue)
        self.assertAlmostEqual(const.yvalue, value.yvalue)
        self.assertAlmostEqual(const.zvalue, value.zvalue)

    def test_typecast_identities(self):
        S = ScalarConstant
        I = IntegerConstant
        B = BooleanConstant

        s = ScalarVar('s')
        i = IntegerVar('i')
        b = BooleanVar('b')

        I2S = ScalarFromInteger
        B2S = ScalarFromBoolean
        S2I = IntegerFromScalar
        B2I = IntegerFromBoolean
        S2B = BooleanFromScalar
        I2B = BooleanFromInteger

        ctx = constant_folding.context()

        # Constant conversions
        self.assertEqual(ctx.get(I2S(I(1))), S(1.0))
        self.assertEqual(ctx.get(B2S(B(True))), S(1.0))

        self.assertEqual(ctx.get(S2I(S(0.0))), I(0))
        self.assertEqual(ctx.get(B2I(B(False))), I(0))
    
        self.assertEqual(ctx.get(S2B(S(0.0))), B(False))
        self.assertEqual(ctx.get(I2B(I(1))), B(True))

        # Chained conversions
        # float->int->float != noop
        self.assertNotEqual(ctx.get(I2S(S2I(s))), s)
        # bool->int->float == bool->float
        self.assertEqual(ctx.get(I2S(B2I(b))), B2S(b))
        # float->bool->float != noop
        self.assertNotEqual(ctx.get(B2S(S2B(s))), s)
        # int->bool->float != int->float
        self.assertNotEqual(ctx.get(B2S(I2B(i))), I2S(i))

        # int->float->int == noop
        self.assertEqual(ctx.get(S2I(I2S(i))), i)
        # bool->float->int == bool->int
        self.assertEqual(ctx.get(S2I(B2S(b))), B2I(b))
        # float->bool->int != float->int
        self.assertNotEqual(ctx.get(B2I(S2B(s))), S2I(s))
        # int->bool->int != noop
        self.assertNotEqual(ctx.get(B2I(I2B(i))), i)

        # int->float->bool == int->bool
        self.assertEqual(ctx.get(S2B(I2S(i))), I2B(i))
        # bool->float->bool == noop
        self.assertEqual(ctx.get(S2B(B2S(b))), b)
        # float->int->bool != float->bool
        self.assertNotEqual(ctx.get(I2B(S2I(s))), S2B(s))
        # bool->int->bool == noop
        self.assertEqual(ctx.get(I2B(B2I(b))), b)

    def test_boolean_operations(self):
        B = BooleanConstant
        ctx = constant_folding.context()
        self.assertEqual(ctx.get(B(True) & B(True)), B(True))
        self.assertEqual(ctx.get(B(True) & B(False)), B(False))
        self.assertEqual(ctx.get(B(False) & B(True)), B(False))
        self.assertEqual(ctx.get(B(False) & B(False)), B(False))
        self.assertEqual(ctx.get(B(True) | B(True)), B(True))
        self.assertEqual(ctx.get(B(True) | B(False)), B(True))
        self.assertEqual(ctx.get(B(False) | B(True)), B(True))
        self.assertEqual(ctx.get(B(False) | B(False)), B(False))
        self.assertEqual(ctx.get(~B(True)), B(False))
        self.assertEqual(ctx.get(~B(False)), B(True))
        self.assertEqual(ctx.get(B(True).eq(B(True))), B(True))
        self.assertEqual(ctx.get(B(True).eq(B(False))), B(False))
        self.assertEqual(ctx.get(B(False).eq(B(True))), B(False))
        self.assertEqual(ctx.get(B(False).eq(B(False))), B(True))
        self.assertEqual(ctx.get(B(True).ne(B(True))), B(False))
        self.assertEqual(ctx.get(B(True).ne(B(False))), B(True))
        self.assertEqual(ctx.get(B(False).ne(B(True))), B(True))
        self.assertEqual(ctx.get(B(False).ne(B(False))), B(False))

    def test_boolean_short_circuit(self):
        B = BooleanConstant
        S = ScalarConstant
        ctx = constant_folding.context()
        zero_div = (S(1) / S(0)).eq(S(0))
        self.assertEqual(ctx.get(B(False) & zero_div), B(False))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(zero_div & B(False)))
        self.assertEqual(ctx.get(B(True) | zero_div), B(True))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(zero_div | B(True)))

    def test_integer_operations(self):
        I = IntegerConstant
        S = ScalarConstant
        ctx = constant_folding.context()
        self.assertEqual(ctx.get(I(2) + I(3)), I(5))
        self.assertEqual(ctx.get(I(2) + S(3.5)), S(5.5))
        self.assertEqual(ctx.get(S(3.5) + I(2)), S(5.5))
        self.assertEqual(ctx.get(I(2) - I(3)), I(-1))
        self.assertEqual(ctx.get(I(2) - S(3.5)), S(-1.5))
        self.assertEqual(ctx.get(S(3.5) - I(2)), S(1.5))
        self.assertEqual(ctx.get(I(2) * I(3)), I(6))
        self.assertEqual(ctx.get(I(2) * S(3.75)), S(7.5))
        self.assertEqual(ctx.get(S(3.75) * I(2)), S(7.5))
        self._assert_scalar_equal(ctx.get(I(1) / I(2)), S(0.5))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(I(1) / I(0)))
        self.assertEqual(ctx.get(I(2) ** I(-3)), S(0.125))
        self._test_comparison_operations(ScalarConstant)

    def test_integer_identities(self):
        self._test_arithmetic_identities(Integer, IntegerConstant)

    def test_scalar_operations(self):
        S = ScalarConstant
        ctx = constant_folding.context()
        self._assert_scalar_equal(ctx.get(S(1.23) + S(4.56)), S(5.79))
        self._assert_scalar_equal(ctx.get(S(1.23) - S(6.54)), S(-5.31))
        self._assert_scalar_equal(ctx.get(S(1.23) * S(-2.4)), S(-2.952))
        self._assert_scalar_equal(ctx.get(S(1.23) / S(2.4)), S(0.5125))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(S(1.23) / S(0)))
        self._assert_scalar_equal(ctx.get(S(1.23) ** S(4.56)), S(2.57020230162))
        self._test_comparison_operations(ScalarConstant)

    def _test_comparison_operations(self, constant_type):
        C = constant_type
        B = BooleanConstant
        ctx = constant_folding.context()
        self.assertEqual(ctx.get(C(1).eq(C(1))), B(True))
        self.assertEqual(ctx.get(C(1) >= C(1)), B(True))
        self.assertEqual(ctx.get(C(2) >= C(1)), B(True))
        self.assertEqual(ctx.get(C(1) >= C(2)), B(False))
        self.assertEqual(ctx.get(C(1) <= C(1)), B(True))
        self.assertEqual(ctx.get(C(2) <= C(1)), B(False))
        self.assertEqual(ctx.get(C(1) <= C(2)), B(True))
        self.assertEqual(ctx.get(C(1).ne(C(1))), B(False))
        self.assertEqual(ctx.get(C(1) > C(1)), B(False))
        self.assertEqual(ctx.get(C(2) > C(1)), B(True))
        self.assertEqual(ctx.get(C(1) > C(2)), B(False))
        self.assertEqual(ctx.get(C(1) < C(1)), B(False))
        self.assertEqual(ctx.get(C(2) < C(1)), B(False))
        self.assertEqual(ctx.get(C(1) < C(2)), B(True))

    def _test_arithmetic_identities(self, base, constant_type):
        class Var(base):
            tag = Field(str)
        a = Var('a')
        T = base
        C = constant_type
        B = BooleanConstant
        ctx = constant_folding.context()

        # Identity a + 0 = a, 0 + a = a
        self.assertEqual(ctx.get(a + C(0)), a)
        self.assertEqual(ctx.get(C(0) + a), a)

        # Identity a - 0 = a
        self.assertEqual(ctx.get(a - C(0)), a)
        self.assertNotEqual(ctx.get(C(0) - a), a)
        # Identity a - a = 0
        self.assertEqual(ctx.get(a - a), C(0))

        # Identity a * 1 = a, 1 * a = a
        self.assertEqual(ctx.get(a * C(1)), a)
        self.assertEqual(ctx.get(C(1) * a), a)
        # Identity a * 0 = 0, 0 * a = 0
        self.assertEqual(ctx.get(a * C(0)), C(0))
        self.assertEqual(ctx.get(C(0) * a), C(0))

        # Identity a / 1 = a
        self.assertEqual(ctx.get(T(a / C(1))), a)
        self.assertNotEqual(ctx.get(T(C(1) / a)), a)
        # Identity 0 / a = 0
        self.assertEqual(ctx.get(T(C(0) / a)), C(0))
        # Identity a / a = 1
        self.assertEqual(ctx.get(T(a / a)), C(1))
        # Zero division
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(a / C(0)))

        # Identity a ** 1 = a
        self.assertEqual(ctx.get(T(a ** C(1))), a)
        # Identity 1 ** a = 1
        self.assertEqual(ctx.get(T(C(1) ** a)), C(1))
        # Identity a ** 0 = 1
        self.assertEqual(ctx.get(T(a ** C(0))), C(1))

        self.assertEqual(ctx.get(a.eq(a)), B(True))
        self.assertEqual(ctx.get(a >= a), B(True))
        self.assertEqual(ctx.get(a <= a), B(True))
        self.assertEqual(ctx.get(a.ne(a)), B(False))
        self.assertEqual(ctx.get(a < a), B(False))
        self.assertEqual(ctx.get(a > a), B(False))

    def test_vector_operations(self):
        S = ScalarConstant
        V = VectorConstant
        ctx = constant_folding.context()
        self._assert_vector_equal(ctx.get(V(0,1,2) + V(3,4,5)), V(3,5,7))
        self._assert_vector_equal(ctx.get(V(0,1,2) - V(5,4,3)), V(-5,-3,-1))
        self._assert_vector_equal(ctx.get(V(1,2,3) * S(2)), V(2,4,6))
        self._assert_vector_equal(ctx.get(V(1,2,3) / S(2)), V(0.5,1.0,1.5))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(V(0,0,0) / S(0)))
        self._assert_scalar_equal(ctx.get(V(1,2,3).length()), S(3.74165738677))
        self._assert_vector_equal(
            ctx.get(V(1,2,3).normalized()),
            V(0.26726124191, 0.53452248382, 0.80178372573),
        )
        self._assert_vector_equal(ctx.get(V(1,2,3).cross(V(4,5,6))), V(-3,6,-3))

    def test_vector_identities(self):
        S = ScalarConstant
        V = VectorConstant
        S2V = VectorFromScalar
    
        a = VectorVar('a')
        i = ScalarVar('i')
        j = ScalarVar('j')
        k = ScalarVar('k')
    
        ctx = constant_folding.context()

        # Composition / component access
        self.assertEqual(ctx.get(S2V(S(0), S(1), S(2))), V(0, 1, 2))
        self.assertEqual(ctx.get(S2V(i,j,k).x), i)
        self.assertEqual(ctx.get(S2V(i,j,k).y), j)
        self.assertEqual(ctx.get(S2V(i,j,k).z), k)
        self.assertEqual(ctx.get(V(0, 1, 2).x), S(0))
        self.assertEqual(ctx.get(V(0, 1, 2).y), S(1))
        self.assertEqual(ctx.get(V(0, 1, 2).z), S(2))

        # a + (0,0,0) = a
        self.assertEqual(ctx.get(V(0,0,0) + a), a)
        # (0,0,0) + a = a
        self.assertEqual(ctx.get(a + V(0,0,0)), a)
    
        # a - (0,0,0) = a
        self.assertEqual(ctx.get(a - V(0,0,0)), a)
        self.assertNotEqual(ctx.get(V(0,0,0) - a), a)

        # a * 1 = a
        self.assertEqual(ctx.get(a * S(1)), a)
        # a * 0 = (0,0,0)
        self.assertEqual(ctx.get(a * S(0)), V(0,0,0))
        # (0,0,0) * k = (0,0,0)
        self.assertEqual(ctx.get(V(0,0,0) * k), V(0,0,0))

        # a / 1 = a
        self.assertEqual(ctx.get(a / S(1)), a)
        # (0,0,0) / k = (0,0,0)
        self.assertEqual(ctx.get(V(0,0,0) / k), V(0,0,0))
        # Division by 0
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(a / S(0)))

        # (0,0,0) * a = 0
        self.assertEqual(ctx.get(V(0,0,0).dot(a)), S(0))
        self.assertEqual(ctx.get(a.dot(V(0,0,0))), S(0))
        # (1,0,0) * (i,j,k) = i
        self.assertEqual(ctx.get(V(1,0,0).dot(S2V(i,j,k))), i)
        self.assertEqual(ctx.get(S2V(i,j,k).dot(V(1,0,0))), i)
        # (0,1,0) * (i,j,k) = j
        self.assertEqual(ctx.get(V(0,1,0).dot(S2V(i,j,k))), j)
        self.assertEqual(ctx.get(S2V(i,j,k).dot(V(0,1,0))), j)
        # (0,0,1) * (i,j,k) = k
        self.assertEqual(ctx.get(V(0,0,1).dot(S2V(i,j,k))), k)
        self.assertEqual(ctx.get(S2V(i,j,k).dot(V(0,0,1))), k)

        # (0,0,0) ^ a = (0,0,0)
        self.assertEqual(ctx.get(V(0,0,0).cross(a)), V(0,0,0))
        self.assertEqual(ctx.get(a.cross(V(0,0,0))), V(0,0,0))
        # a ^ a = (0,0,0)
        self.assertEqual(ctx.get(a.cross(a)), V(0,0,0))

        # |a/|a|| = 1
        self.assertEqual(ctx.get(a.normalized().length()), S(1.0))
        self.assertEqual(ctx.get(a.normalized().normalized()), a.normalized())

    def test_examples(self):
        S = ScalarConstant
        ctx = constant_folding.context()
        example1 = (S(1) + S(2))*(S(7)**S(2) - S(4)/S(3))
        self._assert_scalar_equal(ctx.get(example1), S(143.0))
