from __future__ import division

import unittest

from expy import type_conversions
from expy.expressions.math import *


def _var_type(name, base):
    return type(base)(name, (base,), {"tag": Field(str)})

BooleanVar = _var_type("BooleanVar", Boolean)
IntegerVar = _var_type("IntegerVar", Integer)
ScalarVar = _var_type("ScalarVar", Scalar)
VectorVar = _var_type("VectorVar", Vector)
MatrixVar = _var_type("MatrixVar", Matrix)


class TestMathTypes(unittest.TestCase):

    def test_boolean_constructor(self):
        b = BooleanVar('b')
        self.assertEqual(boolean(), BooleanConstant(False))
        self.assertEqual(boolean(False), BooleanConstant(False))
        self.assertEqual(boolean(True), BooleanConstant(True))
        self.assertEqual(boolean(0), BooleanConstant(False))
        self.assertEqual(boolean(1), BooleanConstant(True))
        self.assertEqual(boolean(2.34), BooleanConstant(True))
        self.assertEqual(boolean(b), b)

    def test_integer_constructor(self):
        i = IntegerVar('i')
        self.assertEqual(integer(), IntegerConstant(False))
        self.assertEqual(integer(False), IntegerConstant(0))
        self.assertEqual(integer(True), IntegerConstant(1))
        self.assertEqual(integer(0), IntegerConstant(0))
        self.assertEqual(integer(1), IntegerConstant(1))
        self.assertEqual(integer(5.67), IntegerConstant(5))
        self.assertEqual(integer(i), i)

    def test_scalar_constructor(self):
        s = ScalarVar('s')
        self.assertEqual(scalar(), ScalarConstant(0.0))
        self.assertEqual(scalar(False), ScalarConstant(0.0))
        self.assertEqual(scalar(True), ScalarConstant(1.0))
        self.assertEqual(scalar(1), ScalarConstant(1.0))
        self.assertEqual(scalar(2.34), ScalarConstant(2.34))
        self.assertEqual(scalar(s), s)

    def test_vector_constructor(self):
        v = VectorVar('v')
        s = ScalarVar('s')
        self.assertEqual(vector(), Vector.ZERO)
        self.assertEqual(vector(1, 2, 3), VectorConstant(1.0, 2.0, 3.0))
        self.assertEqual(vector((1, 2, 3)), VectorConstant(1.0, 2.0, 3.0))
        self.assertEqual(vector([1, 2, 3]), VectorConstant(1.0, 2.0, 3.0))
        self.assertEqual(vector(s, 2, 3), VectorFromScalar(s, 2.0, 3.0))
        self.assertEqual(vector((s, 2, 3)), VectorFromScalar(s, 2.0, 3.0))
        self.assertEqual(vector([s, 2, 3]), VectorFromScalar(s, 2.0, 3.0))
        self.assertRaises(TypeError, lambda: vector(1, 2, 3, 4))
        self.assertRaises(TypeError, lambda: vector((1, 2, 3, 4)))
        self.assertRaises(TypeError, lambda: vector([1, 2, 3, 4]))
        self.assertEqual(vector(v), v)

    def test_matrix_constructor(self):
        m = MatrixVar('m')
        s = ScalarVar('s')
        self.assertEqual(matrix(), Matrix.IDENTITY)
        self.assertEqual(matrix(*range(16)), MatrixConstant(*range(16)))
        self.assertEqual(
            matrix(s,0,0,0,0,s,0,0,0,0,s,0,0,0,0,s),
            MatrixFromScalar(s,0,0,0,0,s,0,0,0,0,s,0,0,0,0,s),
        )
        self.assertEqual(
            matrix([s,0,0,0,0,s,0,0,0,0,s,0,0,0,0,s]),
            MatrixFromScalar(s,0,0,0,0,s,0,0,0,0,s,0,0,0,0,s),
        )
        self.assertEqual(
            matrix([s,0,0,0],[0,s,0,0],[0,0,s,0],[0,0,0,s]),
            MatrixFromScalar(s,0,0,0,0,s,0,0,0,0,s,0,0,0,0,s),
        )
        self.assertEqual(
            matrix(((2,0,0,0),(0,2,0,0),(0,0,2,0),(0,0,0,2))),
            MatrixConstant(2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2),
        )
        self.assertEqual(matrix(m), m)

    def test_boolean_type_identities(self):
        b = BooleanVar('b')
        i = IntegerVar('i')
        s = ScalarVar('s')

        self.assertIsInstance(b | b, Boolean)
        self.assertIsInstance(b | i, Boolean)
        self.assertIsInstance(b | s, Boolean)
        self.assertIsInstance(b | True, Boolean)
        self.assertIsInstance(i | b, Boolean)
        self.assertIsInstance(s | b, Boolean)
        self.assertIsInstance(False | b, Boolean)

        self.assertIsInstance(b & b, Boolean)
        self.assertIsInstance(b & i, Boolean)
        self.assertIsInstance(b & s, Boolean)
        self.assertIsInstance(b & True, Boolean)
        self.assertIsInstance(i & b, Boolean)
        self.assertIsInstance(s & b, Boolean)
        self.assertIsInstance(False & b, Boolean)

    def test_integer_type_identities(self):
        b = BooleanVar('b')
        i = IntegerVar('i')
        s = ScalarVar('s')
        v = VectorVar('v')
        m = MatrixVar('m')

        self.assertIsInstance(i + i, Integer)
        self.assertIsInstance(i + b, Integer)
        self.assertIsInstance(i + s, Scalar)
        self.assertIsInstance(i + 1, Integer)
        self.assertIsInstance(b + i, Integer)
        self.assertIsInstance(1 + i, Integer)
        self.assertIsInstance(1.0 + i, Scalar)

        self.assertIsInstance(i - i, Integer)
        self.assertIsInstance(i - b, Integer)
        self.assertIsInstance(i - s, Scalar)
        self.assertIsInstance(i - 1, Integer)
        self.assertIsInstance(b - i, Integer)
        self.assertIsInstance(1 - i, Integer)
        self.assertIsInstance(1.0 - i, Scalar)

        self.assertIsInstance(i * i, Integer)
        self.assertIsInstance(i * b, Integer)
        self.assertIsInstance(i * s, Scalar)
        self.assertIsInstance(i * v, Vector)
        self.assertIsInstance(i * m, Matrix)
        self.assertIsInstance(i * 2, Integer)
        self.assertIsInstance(b * i, Integer)
        self.assertIsInstance(2 * i, Integer)
        self.assertIsInstance(2.0 * i, Scalar)

        self.assertIsInstance(i / i, Scalar)
        self.assertIsInstance(i / 2, Scalar)
        self.assertIsInstance(b / i, Scalar)
        self.assertIsInstance(2 / i, Scalar)

        self.assertIsInstance(i ** i, Scalar)
        self.assertIsInstance(i ** b, Scalar)
        self.assertIsInstance(i ** s, Scalar)
        self.assertIsInstance(i ** 2, Scalar)
        self.assertIsInstance(b ** i, Scalar)
        self.assertIsInstance(2 ** i, Scalar)

        self.assertIsInstance(-i, Integer)

    def test_scalar_type_identities(self):
        b = BooleanVar('b')
        i = IntegerVar('i')
        s = ScalarVar('s')
        v = VectorVar('v')
        m = MatrixVar('m')

        self.assertIsInstance(s + s, Scalar)
        self.assertIsInstance(s + i, Scalar)
        self.assertIsInstance(s + b, Scalar)
        self.assertIsInstance(s + 1.0, Scalar)
        self.assertIsInstance(1.0 + s, Scalar)
        self.assertIsInstance(b + s, Scalar)

        self.assertIsInstance(s - s, Scalar)
        self.assertIsInstance(s - i, Scalar)
        self.assertIsInstance(s - b, Scalar)
        self.assertIsInstance(s - 1.0, Scalar)
        self.assertIsInstance(1.0 - s, Scalar)
        self.assertIsInstance(b - s, Scalar)

        self.assertIsInstance(s * s, Scalar)
        self.assertIsInstance(s * i, Scalar)
        self.assertIsInstance(s * b, Scalar)
        self.assertIsInstance(s * v, Vector)
        self.assertIsInstance(s * m, Matrix)
        self.assertIsInstance(s * 2.0, Scalar)
        self.assertIsInstance(2.0 * s, Scalar)
        self.assertIsInstance(b * s, Scalar)

        self.assertIsInstance(s / s, Scalar)
        self.assertIsInstance(s / i, Scalar)
        self.assertIsInstance(s / b, Scalar)
        self.assertIsInstance(1.0 / s, Scalar)
        self.assertIsInstance(b / s, Scalar)
        self.assertRaises(TypeError, lambda: s / v)
        self.assertRaises(TypeError, lambda: s / m)

        self.assertIsInstance(s ** s, Scalar)
        self.assertIsInstance(s ** i, Scalar)
        self.assertIsInstance(s ** b, Scalar)
        self.assertIsInstance(s ** 2.0, Scalar)
        self.assertIsInstance(2.0 ** s, Scalar)
        self.assertIsInstance(b ** s, Scalar)
        self.assertRaises(TypeError, lambda: s ** v)
        self.assertRaises(TypeError, lambda: s ** m)

        self.assertIsInstance(-s, Scalar)

    def test_vector_type_identities(self):
        b = BooleanVar('b')
        i = IntegerVar('i')
        s = ScalarVar('s')
        v = VectorVar('v')
        m = MatrixVar('m')

        self.assertIsInstance(v + v, Vector)
        self.assertRaises(TypeError, lambda: v + b)
        self.assertRaises(TypeError, lambda: v + i)
        self.assertRaises(TypeError, lambda: v + s)
        self.assertRaises(TypeError, lambda: v + m)

        self.assertIsInstance(v - v, Vector)
        self.assertRaises(TypeError, lambda: v - b)
        self.assertRaises(TypeError, lambda: v - i)
        self.assertRaises(TypeError, lambda: v - s)
        self.assertRaises(TypeError, lambda: v - m)

        self.assertIsInstance(v * b, Vector)
        self.assertIsInstance(v * i, Vector)
        self.assertIsInstance(v * s, Vector)
        self.assertIsInstance(v * m, Vector)
        self.assertIsInstance(v * 2.0, Vector)
        self.assertRaises(TypeError, lambda: v * v)

        self.assertIsInstance(v / b, Vector)
        self.assertIsInstance(v / i, Vector)
        self.assertIsInstance(v / s, Vector)
        self.assertIsInstance(v / 2.0, Vector)
        self.assertRaises(TypeError, lambda: v / m)

        self.assertIsInstance(-v, Vector)

    def test_matrix_type_identities(self):
        b = BooleanVar('b')
        i = IntegerVar('i')
        s = ScalarVar('s')
        v = VectorVar('v')
        m = MatrixVar('m')

        self.assertIsInstance(m + m, Matrix)
        self.assertRaises(TypeError, lambda: m + b)
        self.assertRaises(TypeError, lambda: m + i)
        self.assertRaises(TypeError, lambda: m + s)
        self.assertRaises(TypeError, lambda: m + v)

        self.assertIsInstance(m - m, Matrix)
        self.assertRaises(TypeError, lambda: m - b)
        self.assertRaises(TypeError, lambda: m - i)
        self.assertRaises(TypeError, lambda: m - s)
        self.assertRaises(TypeError, lambda: m - v)

        self.assertIsInstance(m * b, Matrix)
        self.assertIsInstance(m * i, Matrix)
        self.assertIsInstance(m * s, Matrix)
        self.assertIsInstance(m * v, Vector)
        self.assertIsInstance(m * m, Matrix)
        self.assertIsInstance(m * 2.0, Matrix)

        self.assertIsInstance(m / b, Matrix)
        self.assertIsInstance(m / i, Matrix)
        self.assertIsInstance(m / s, Matrix)
        self.assertIsInstance(m / 2.0, Matrix)
        self.assertRaises(TypeError, lambda: m / m)
        self.assertRaises(TypeError, lambda: m / v)

        self.assertIsInstance(-m, Matrix)


if __name__ == '__main__':
    unittest.main()
