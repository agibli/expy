from __future__ import division

import unittest

from expy import type_conversions
from expy.expressions.math import *
from expy.contexts.constant_folding import ConstantFoldingContext


def _var_type(name, base):
    return type(base)(name, (base,), {"tag": Field(str)})

BooleanVar = _var_type("BooleanVar", Boolean)
IntegerVar = _var_type("IntegerVar", Integer)
ScalarVar = _var_type("ScalarVar", Scalar)
VectorVar = _var_type("VectorVar", Vector)
MatrixVar = _var_type("MatrixVar", Matrix)


class TestConstantFolding(unittest.TestCase):

    def _assert_scalar_equal(self, const, value):
        self.assertIsInstance(const, ScalarConstant)
        self.assertAlmostEqual(const.value, value.value)

    def _assert_vector_equal(self, const, value):
        self.assertIsInstance(const, VectorConstant)
        self.assertAlmostEqual(const.xvalue, value.xvalue)
        self.assertAlmostEqual(const.yvalue, value.yvalue)
        self.assertAlmostEqual(const.zvalue, value.zvalue)

    def _assert_matrix_equal(self, const, value):
        self.assertIsInstance(const, MatrixConstant)
        for a, b in zip(const._values, value._values):
            self.assertAlmostEqual(a, b)

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

        ctx = ConstantFoldingContext()

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
        ctx = ConstantFoldingContext()
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
        ctx = ConstantFoldingContext()
        zero_div = (S(1) / S(0)).eq(S(0))
        self.assertEqual(ctx.get(B(False) & zero_div), B(False))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(zero_div & B(False)))
        self.assertEqual(ctx.get(B(True) | zero_div), B(True))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(zero_div | B(True)))

    def test_integer_operations(self):
        I = IntegerConstant
        S = ScalarConstant
        ctx = ConstantFoldingContext()
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
        ctx = ConstantFoldingContext()
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
        ctx = ConstantFoldingContext()
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
        T = type_conversions.constructor(base)
        C = constant_type
        B = BooleanConstant
        ctx = ConstantFoldingContext()

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
        ctx = ConstantFoldingContext()
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
    
        ctx = ConstantFoldingContext()

        # Composition / component access
        self.assertEqual(ctx.get(S2V(S(0), S(1), S(2))), V(0, 1, 2))
        self.assertEqual(ctx.get(S2V(i,j,k).x), i)
        self.assertEqual(ctx.get(S2V(i,j,k).y), j)
        self.assertEqual(ctx.get(S2V(i,j,k).z), k)
        self.assertEqual(ctx.get(V(0, 1, 2).x), S(0))
        self.assertEqual(ctx.get(V(0, 1, 2).y), S(1))
        self.assertEqual(ctx.get(V(0, 1, 2).z), S(2))
        self.assertEqual(ctx.get(S2V(a.x,a.y,a.z)), a)

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

    def test_matrix_operations(self):
        S = ScalarConstant
        V = VectorConstant
        M = MatrixConstant
        zero = Matrix.ZERO
        m1 = M(
            -1.47562898915, 7.73892261048, -0.636700193883, -7.27511191565,
            -9.13895323721, 7.73574129521, 0.973591335962, 3.01430692063,
            -4.91771153978, 5.60402612802, 2.96411112361, -3.85652185424,
            -6.42222719512, 3.00731946438, 3.73596052196, 7.00422507133,
        )
        m2 = M(
            -7.71598902963, -5.24995175379, 3.50941987372, 6.68985402811,
            9.78184029315, 1.03546950178, 3.23483519687, -8.26166456441,
            -9.12516377997, -6.51115202518, 9.42557887812, -6.06548190021,
            -0.988702568204, 3.89587352648, -2.11375664001, 7.68922813683,
        )
        v = V(4.4925060373, 3.54494750813, 2.96842936979)
        s = S(7.215897398019421)

        ctx = ConstantFoldingContext()
        self._assert_matrix_equal(ctx.get(m1 * s), M(
            -10.6479873832, 55.8432715285, -4.59436327236, -52.4964611424,
            -65.945748885, 55.8203154839, 7.0253351879, 21.7509294654,
            -35.4857019041, 40.4380775556, 21.3887217443, -27.8282660134,
            -46.3421325068, 21.700508698, 26.9583078095, 50.5417694673,
        ))
        self._assert_matrix_equal(ctx.get(s * m1), M(
            -10.6479873832, 55.8432715285, -4.59436327236, -52.4964611424,
            -65.945748885, 55.8203154839, 7.0253351879, 21.7509294654,
            -35.4857019041, 40.4380775556, 21.3887217443, -27.8282660134,
            -46.3421325068, 21.700508698, 26.9583078095, 50.5417694673,
        ))
        self._assert_vector_equal(ctx.get(m1 * v), V(
            18.9148027258, -10.7439686488, 6.57188419054,
        ))
        self._assert_vector_equal(ctx.get(v * m1), V(
            -53.6242610146, 78.8251091253, 9.38970523003,
        ))
        self._assert_matrix_equal(ctx.get(m1 * m2), M(
            100.089757492, -8.43686481819, 29.2320857648, -125.886226973,
            134.32141543, 61.3933450942, -4.24342523643, -107.775969904,
            69.5276504714, -2.70375307595, 36.959998228, -126.829795156,
            37.9546063397, 39.7925386241, 7.59825443211, -36.6125435541,
        ))
        self._assert_matrix_equal(ctx.get(m1 / s), M(
            -0.204496947193, 1.07248235162, -0.0882357604, -1.00820611968,
            -1.26650265838, 1.07204147572, 0.134923112436, 0.417731399765,
            -0.681510735051, 0.776622202189, 0.410775120558, -0.534447989144,
            -0.890010880266, 0.416763057801, 0.51774024988, 0.970665834751,
        ))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(m1 / S(0)))
        self._assert_matrix_equal(ctx.get(m1.transpose()), M(
            -1.47562898915, -9.13895323721, -4.91771153978, -6.42222719512,
            7.73892261048, 7.73574129521, 5.60402612802, 3.00731946438,
            -0.636700193883, 0.973591335962, 2.96411112361, 3.73596052196,
            -7.27511191565, 3.01430692063, -3.85652185424, 7.00422507133,
        ))
        self._assert_matrix_equal(ctx.get(m1.inverse()), M(
            0.281024696013, -0.235732671287, -0.211321985613, 0.276988369374,
            0.284247540149, -0.102538645986, -0.19658076917, 0.231131576677,
            0.0621626854628, -0.248632919398, 0.12759620531, 0.241821751929,
            0.102472998641, -0.0395018053024, -0.177417344905, 0.168521031032,
        ))
        self.assertRaises(ZeroDivisionError, lambda: ctx.get(zero.inverse()))

    def test_matrix_identities(self):
        S = ScalarConstant
        V = VectorConstant
        M = MatrixConstant
        S2M = MatrixFromScalar

        a = MatrixVar('a')
        u = VectorVar('u')
        k = ScalarVar('k')
        zero = Matrix.ZERO
        ident = Matrix.IDENTITY

        ctx = ConstantFoldingContext()

        # Composition / component access
        s2m = S2M(*(
            ScalarVar("a{}{}".format(i,j)) for i in range(4) for j in range(4)
        ))
        for i in range(4):
            for j in range(4):
                self.assertEqual(
                    ctx.get(s2m[i,j]),
                    getattr(s2m, "a{}{}".format(i,j))
                )

        # a + (0) = a
        self.assertEqual(ctx.get(a + zero), a)
        self.assertEqual(ctx.get(zero + a), a)

        # a - (0) = a
        self.assertEqual(ctx.get(a - zero), a)
        self.assertNotEqual(ctx.get(zero - a), a)
        # a - a = (0)
        self._assert_matrix_equal(ctx.get(a - a), zero)

        # a * 0 = (0)
        self._assert_matrix_equal(ctx.get(a * 0), zero)
        self._assert_matrix_equal(ctx.get(0 * a), zero)
        # a * 1 = a
        self.assertEqual(ctx.get(a * 1), a)
        self.assertEqual(ctx.get(1 * a), a)
        # (0) * k = (k)
        self._assert_matrix_equal(ctx.get(zero * k), zero)
        self._assert_matrix_equal(ctx.get(k * zero), zero)

        # a * (0) = (0)
        self._assert_matrix_equal(ctx.get(a * zero), zero)
        self._assert_matrix_equal(ctx.get(zero * a), zero)
        # a * I = a
        self.assertEqual(ctx.get(a * ident), a)
        self.assertEqual(ctx.get(ident * a), a)
        # a * a^-1 = I
        self._assert_matrix_equal(ctx.get(a * a.inverse()), ident)
        self._assert_matrix_equal(ctx.get(a.inverse() * a), ident)

        # a * (0,0,0) = (0,0,0)
        self._assert_vector_equal(ctx.get(a * V(0,0,0)), V(0,0,0))
        self._assert_vector_equal(ctx.get(V(0,0,0) * a), V(0,0,0))
        # (0) * u = (0,0,0)
        self._assert_vector_equal(ctx.get(zero * u), V(0,0,0))
        self._assert_vector_equal(ctx.get(u * zero), V(0,0,0))
        # I * u = u
        self.assertEqual(ctx.get(ident * u), u)
        self.assertEqual(ctx.get(u * ident), u)

        # a / 1 = a
        self.assertEqual(ctx.get(a / 1), a)
        # (0) / k = (0)
        self._assert_matrix_equal(ctx.get(zero / k), zero)

        # (a^T)^T = a
        self.assertEqual(ctx.get(a.transpose().transpose()), a)
        # (a^-1)^-1 = a
        self.assertEqual(ctx.get(a.inverse().inverse()), a)

    def test_examples(self):
        S = ScalarConstant
        ctx = ConstantFoldingContext()
        example1 = (S(1) + S(2))*(S(7)**S(2) - S(4)/S(3))
        self._assert_scalar_equal(ctx.get(example1), S(143.0))


if __name__ == '__main__':
    unittest.main()
