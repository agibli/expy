from __future__ import absolute_import, division

import math
import operator
import functools

from ...expressions.math import *
from .context import constant_folding


def _handle_unary_op(constant_type, func, context, expression):
    operand = context.get(expression.operand)
    if isinstance(operand, constant_type):
        return constant_type(func(operand.value))
    return type(expression)(operand)


def _handle_binary_op(constant_type, func, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return constant_type(func(left.value, right.value))
    return type(expression)(left, right)


constant_folding.register_handler(
    BooleanInverse, functools.partial(_handle_unary_op, BooleanConstant, operator.not_)
)
constant_folding.register_handler(
    BooleanEquals, functools.partial(_handle_binary_op, BooleanConstant, operator.eq)
)
constant_folding.register_handler(
    BooleanNotEquals, functools.partial(_handle_binary_op, BooleanConstant, operator.ne)
)


@constant_folding.handler(BooleanAnd)
def _handle_boolean_and(context, expression):
    left = context.get(expression.loperand)
    if left == BooleanConstant(False):
        return BooleanConstant(False)
    right = context.get(expression.roperand)
    if isinstance(left, BooleanConstant) and isinstance(right, BooleanConstant):
        return BooleanConstant(left.value and right.value)
    elif right == BooleanConstant(False):
        return BooleanConstant(False)
    return BooleanAnd(left, right)


@constant_folding.handler(BooleanOr)
def _handle_boolean_or(context, expression):
    left = context.get(expression.loperand)
    if left == BooleanConstant(True):
        return BooleanConstant(True)
    right = context.get(expression.roperand)
    if isinstance(left, BooleanConstant) and isinstance(right, BooleanConstant):
        return BooleanConstant(left.value or right.value)
    elif right == BooleanConstant(True):
        return BooleanConstant(True)
    return BooleanOr(left, right)


@constant_folding.handler(ScalarFromInteger)
def _handle_scalar_from_integer(context, expression):
    value = context.get(expression.value)
    if isinstance(value, IntegerConstant):
        return ScalarConstant(float(value.value))
    elif isinstance(value, IntegerFromBoolean):
        return ScalarFromBoolean(value.value)
    return ScalarFromInteger(value)


@constant_folding.handler(ScalarFromBoolean)
def _handle_scalar_from_boolean(context, expression):
    value = context.get(expression.value)
    if isinstance(value, BooleanConstant):
        return ScalarConstant(float(value.value))
    return ScalarFromBoolean(value)


@constant_folding.handler(IntegerFromScalar)
def _handle_integer_from_scalar(context, expression):
    value = context.get(expression.value)
    if isinstance(value, ScalarConstant):
        return IntegerConstant(int(value.value))
    elif isinstance(value, ScalarFromInteger):
        return value.value
    elif isinstance(value, ScalarFromBoolean):
        return IntegerFromBoolean(value.value)
    return IntegerFromScalar(value)


@constant_folding.handler(IntegerFromBoolean)
def _handle_integer_from_boolean(context, expression):
    value = context.get(expression.value)
    if isinstance(value, BooleanConstant):
        return IntegerConstant(int(value.value))
    return IntegerFromBoolean(value)


@constant_folding.handler(BooleanFromScalar)
def _handle_boolean_from_scalar(context, expression):
    value = context.get(expression.value)
    if isinstance(value, ScalarConstant):
        return BooleanConstant(bool(value.value))
    elif isinstance(value, ScalarFromBoolean):
        return value.value
    elif isinstance(value, ScalarFromInteger):
        return BooleanFromInteger(value.value)
    return BooleanFromScalar(value)


@constant_folding.handler(BooleanFromInteger)
def _handle_boolean_from_integer(context, expression):
    value = context.get(expression.value)
    if isinstance(value, IntegerConstant):
        return BooleanConstant(bool(value.value))
    elif isinstance(value, IntegerFromBoolean):
        return value.value
    return BooleanFromInteger(value)


def _handle_add(constant_type, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return constant_type(left.value + right.value)
    elif left == constant_type(0):
        # Identity: 0 + a = a
        return right
    elif right == constant_type(0):
        # Identity: a + 0 = a
        return left
    return type(expression)(left, right)

constant_folding.register_handler(
    ScalarAdd, functools.partial(_handle_add, ScalarConstant)
)
constant_folding.register_handler(
    IntegerAdd, functools.partial(_handle_add, IntegerConstant)
)


def _handle_subtract(constant_type, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return constant_type(left.value - right.value)
    elif right == constant_type(0):
        # Identity: a - 0 = a
        return left
    elif left == right:
        # Identity: a - a = 0
        return constant_type(0)
    return type(expression)(left, right)

constant_folding.register_handler(
    ScalarSubtract, functools.partial(_handle_subtract, ScalarConstant)
)
constant_folding.register_handler(
    IntegerSubtract, functools.partial(_handle_subtract, IntegerConstant)
)


def _handle_multiply(constant_type, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return constant_type(left.value * right.value)
    elif left == constant_type(1):
        # Identity: 1 * a = a
        return right
    elif right == constant_type(1):
        # Identity: a * 1 = a
        return left
    elif left == constant_type(0):
        # Identity: 0 * a = 0
        return left
    elif right == constant_type(0):
        # Identity: a * 0 = 0
        return right
    return type(expression)(left, right)

constant_folding.register_handler(
    ScalarMultiply, functools.partial(_handle_multiply, ScalarConstant)
)
constant_folding.register_handler(
    IntegerMultiply, functools.partial(_handle_multiply, IntegerConstant)
)


def _handle_divide(constant_type, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return constant_type(left.value / right.value)
    elif right == constant_type(1):
        # Identity: a / 1 = a
        return left
    elif left == constant_type(0):
        # Identity: 0 / a = 0 (a != 0)
        return left
    elif right == constant_type(0):
        # Identity: 0 / a = 0 (a != 0)
        raise ZeroDivisionError
    elif left == right:
        # Identity: a / a = 1 (a != 0)
        return constant_type(1)
    return type(expression)(left, right)

constant_folding.register_handler(
    ScalarDivide, functools.partial(_handle_divide, ScalarConstant)
)
constant_folding.register_handler(
    IntegerDivide, functools.partial(_handle_divide, IntegerConstant)
)


def _handle_power(constant_type, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return constant_type(left.value ** right.value)
    elif right == constant_type(1):
        # Identity: a ** 1 = a
        return left
    elif right == constant_type(0):
        # Identity: a ** 0 = 1
        return constant_type(1)
    elif left == constant_type(1):
        # Identity: 1 ** a = 1
        return left
    return type(expression)(left, right)

constant_folding.register_handler(
    ScalarPower, functools.partial(_handle_power, ScalarConstant)
)


def _handle_equals(constant_type, func, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return BooleanConstant(func(left.value, right.value))
    elif left == right:
        return BooleanConstant(True)
    return type(expression)(left, right)


constant_folding.register_handler(
    IntegerEquals, functools.partial(_handle_equals, IntegerConstant, operator.eq)
)
constant_folding.register_handler(
    IntegerLessThanEquals, functools.partial(_handle_equals, IntegerConstant, operator.le)
)
constant_folding.register_handler(
    IntegerGreaterThanEquals, functools.partial(_handle_equals, IntegerConstant, operator.ge)
)

constant_folding.register_handler(
    ScalarEquals, functools.partial(_handle_equals, ScalarConstant, operator.eq)
)
constant_folding.register_handler(
    ScalarLessThanEquals, functools.partial(_handle_equals, ScalarConstant, operator.le)
)
constant_folding.register_handler(
    ScalarGreaterThanEquals, functools.partial(_handle_equals, ScalarConstant, operator.ge)
)


def _handle_not_equals(constant_type, func, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, constant_type) and isinstance(right, constant_type):
        return BooleanConstant(func(left.value, right.value))
    elif left == right:
        return BooleanConstant(False)
    return type(expression)(left, right)


constant_folding.register_handler(
    IntegerNotEquals, functools.partial(_handle_not_equals, IntegerConstant, operator.ne)
)
constant_folding.register_handler(
    IntegerLessThan, functools.partial(_handle_not_equals, IntegerConstant, operator.lt)
)
constant_folding.register_handler(
    IntegerGreaterThan, functools.partial(_handle_not_equals, IntegerConstant, operator.gt)
)

constant_folding.register_handler(
    ScalarNotEquals, functools.partial(_handle_not_equals, ScalarConstant, operator.ne)
)
constant_folding.register_handler(
    ScalarLessThan, functools.partial(_handle_not_equals, ScalarConstant, operator.lt)
)
constant_folding.register_handler(
    ScalarGreaterThan, functools.partial(_handle_not_equals, ScalarConstant, operator.gt)
)


@constant_folding.handler(VectorComponent)
def _handle_vector_component(context, expression):
    vector = context.get(expression.value)
    index = expression.index
    if isinstance(vector, VectorFromScalar):
        return vector._values[index]
    if isinstance(vector, VectorConstant):
        return ScalarConstant(vector._values[index])
    return VectorComponent(vector, index)


@constant_folding.handler(VectorFromScalar)
def _handle_vector_from_scalar(context, expression):
    x = context.get(expression.x)
    y = context.get(expression.y)
    z = context.get(expression.z)
    if (
        isinstance(x, ScalarConstant)
        and isinstance(y, ScalarConstant)
        and isinstance(z, ScalarConstant)
    ):
        return VectorConstant(x, y, z)
    # (a.x, a.y, a.z) == a
    if (
        isinstance(x, VectorComponent) and x.index == 0
        and isinstance(y, VectorComponent) and y.index == 1
        and isinstance(z, VectorComponent) and z.index == 2
    ):
        a = context.get(x.value)
        b = context.get(y.value)
        c = context.get(z.value)
        if a == b == c:
            return a
    return VectorFromScalar(x, y, z)


@constant_folding.handler(VectorAdd)
def _handle_vector_add(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, VectorConstant) and isinstance(right, VectorConstant):
        return VectorConstant(
            left.xvalue + right.xvalue,
            left.yvalue + right.yvalue,
            left.zvalue + right.zvalue,
        )
    elif left == VectorConstant(0, 0, 0):
        return right
    elif right == VectorConstant(0, 0, 0):
        return left
    return VectorAdd(left, right)


@constant_folding.handler(VectorSubtract)
def _handle_vector_subtract(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, VectorConstant) and isinstance(right, VectorConstant):
        return VectorConstant(
            left.xvalue - right.xvalue,
            left.yvalue - right.yvalue,
            left.zvalue - right.zvalue,
        )
    elif right == VectorConstant(0, 0, 0):
        return left
    return VectorSubtract(left, right)


@constant_folding.handler(VectorMultiply)
def _handle_vector_multiply(context, expression):
    vector = context.get(expression.loperand)
    scalar = context.get(expression.roperand)
    if isinstance(vector, VectorConstant) and isinstance(scalar, ScalarConstant):
        return VectorConstant(
            vector.xvalue * scalar.value,
            vector.yvalue * scalar.value,
            vector.zvalue * scalar.value,
        )
    elif scalar == ScalarConstant(1):
        return vector
    elif scalar == ScalarConstant(0):
        return VectorConstant(0, 0, 0)
    elif vector == VectorConstant(0, 0, 0):
        return VectorConstant(0, 0, 0)
    return VectorMultiply(vector, scalar)


@constant_folding.handler(VectorDivide)
def _handle_vector_divide(context, expression):
    vector = context.get(expression.loperand)
    scalar = context.get(expression.roperand)
    if isinstance(vector, VectorConstant) and isinstance(scalar, ScalarConstant):
        return VectorConstant(
            vector.xvalue / scalar.value,
            vector.yvalue / scalar.value,
            vector.zvalue / scalar.value,
        )
    elif scalar == ScalarConstant(1):
        return vector
    elif scalar == ScalarConstant(0):
        raise ZeroDivisionError
    elif vector == VectorConstant(0, 0, 0):
        return vector
    return VectorDivide(vector, scalar)


@constant_folding.handler(VectorDotProduct)
def _handle_dot_product(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, VectorConstant) and isinstance(right, VectorConstant):
        return ScalarConstant(
            left.xvalue * right.xvalue
            + left.yvalue * right.yvalue
            + left.zvalue * right.zvalue
        )
    elif left == VectorConstant(0, 0, 0) or right == VectorConstant(0, 0, 0):
        return ScalarConstant(0)
    for a, b in ((left, right), (right, left)):
        if a == VectorConstant(1, 0, 0) and isinstance(b, VectorFromScalar):
            # Identity: (1,0,0)*(x,y,z) = x
            return b.x
        elif a == VectorConstant(0, 1, 0) and isinstance(b, VectorFromScalar):
            # Identity: (0,1,0)*(x,y,z) = y
            return b.y
        elif a == VectorConstant(0, 0, 1) and isinstance(b, VectorFromScalar):
            # Identity: (0,0,1)*(x,y,z) = z
            return b.z
    return VectorDotProduct(left, right)


@constant_folding.handler(VectorCrossProduct)
def _handle_cross_product(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, VectorConstant) and isinstance(right, VectorConstant):
        return VectorConstant(
            left.yvalue * right.zvalue - left.zvalue * right.yvalue,
            left.zvalue * right.xvalue - left.xvalue * right.zvalue,
            left.xvalue * right.yvalue - left.yvalue * right.xvalue,
        )
    elif (
        left == right
        or left == VectorConstant(0, 0, 0)
        or right == VectorConstant(0, 0, 0)
    ):
        return VectorConstant(0, 0, 0)
    return VectorCrossProduct(left, right)


@constant_folding.handler(VectorNormalize)
def _handle_vector_normalize(context, expression):
    vector = context.get(expression.operand)
    if isinstance(vector, VectorConstant):
        length = math.sqrt(
            vector.xvalue * vector.xvalue
            + vector.yvalue * vector.yvalue
            + vector.zvalue * vector.zvalue
        )
        return VectorConstant(
            vector.xvalue / length,
            vector.yvalue / length,
            vector.zvalue / length,
        )
    elif isinstance(vector, VectorNormalize):
        return vector
    return VectorNormalize(vector)


@constant_folding.handler(VectorLength)
def _handle_vector_length(context, expression):
    vector = context.get(expression.operand)
    if isinstance(vector, VectorConstant):
        return ScalarConstant(
            math.sqrt(
                vector.xvalue * vector.xvalue
                + vector.yvalue * vector.yvalue
                + vector.zvalue * vector.zvalue
            )
        )
    elif isinstance(vector, VectorNormalize):
        return ScalarConstant(1.0)
    return VectorLength(vector)


@constant_folding.handler(MatrixFromScalar)
def _handle_scalar_to_matrix(context, expression):
    scalars = [context.get(a) for a in expression._values]
    if all(isinstance(s, ScalarConstant) for s in scalars):
        return MatrixConstant(*(s.value for s in scalars))
    return MatrixFromScalar(*scalars)


@constant_folding.handler(MatrixComponent)
def _handle_matrix_component(context, expression):
    value = context.get(expression.value)
    i = expression.row
    j = expression.column
    if isinstance(value, MatrixConstant) or isinstance(value, MatrixFromScalar):
        return value[i,j]
    return MatrixComponent(value, i, j)


@constant_folding.handler(MatrixAdd)
def _handle_matrix_add(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, MatrixConstant) and isinstance(right, MatrixConstant):
        return MatrixConstant(
            *(a + b for a,b in zip(left._values, right._values))
        )
    elif left == Matrix.ZERO:
        return right
    elif right == Matrix.ZERO:
        return left
    return MatrixAdd(left, right)


@constant_folding.handler(MatrixSubtract)
def _handle_matrix_subtract(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, MatrixConstant) and isinstance(right, MatrixConstant):
        return MatrixConstant(
            *(a - b for a,b in zip(left._values, right._values))
        )
    if right == Matrix.ZERO:
        return left
    elif left == right:
        return Matrix.ZERO
    return MatrixSubtract(left, right)


@constant_folding.handler(MatrixScalarMultiply)
def _handle_matrix_scalar_multiply(context, operator):
    matrix = context.get(operator.loperand)
    scalar = context.get(operator.roperand)
    if isinstance(matrix, MatrixConstant) and isinstance(scalar, ScalarConstant):
        return MatrixConstant(*(a * scalar.value for a in matrix._values))
    elif scalar == ScalarConstant(1):
        return matrix
    elif scalar == ScalarConstant(0) or matrix == Matrix.ZERO:
        return Matrix.ZERO
    return MatrixScalarMultiply(matrix, scalar)


@constant_folding.handler(MatrixDivide)
def _handle_matrix_divide(context, operator):
    matrix = context.get(operator.loperand)
    scalar = context.get(operator.roperand)
    if isinstance(matrix, MatrixConstant) and isinstance(scalar, ScalarConstant):
        s = scalar.value
        return MatrixConstant(*(a / s for a in matrix._values))
    elif scalar == ScalarConstant(1):
        return matrix
    elif scalar == ScalarConstant(0):
        raise ZeroDivisionError
    elif matrix == Matrix.ZERO:
        return Matrix.ZERO
    return MatrixDivide(matrix, scalar)


@constant_folding.handler(MatrixVectorMultiply)
def _handle_matrix_vector_multiply(context, expression):
    matrix = context.get(expression.loperand)
    vector = context.get(expression.roperand)
    if isinstance(matrix, MatrixConstant) and isinstance(vector, VectorConstant):
        x, y, z = vector._values
        return VectorConstant(
            x*matrix.a00 + y*matrix.a01 + z*matrix.a02,
            x*matrix.a10 + y*matrix.a11 + z*matrix.a12,
            x*matrix.a20 + y*matrix.a21 + z*matrix.a22,
        )
    elif vector == VectorConstant(0, 0, 0) or matrix == Matrix.IDENTITY:
        return vector
    elif matrix == Matrix.ZERO:
        return VectorConstant(0, 0, 0)
    return VectorMatrixMultiply(vector, matrix)


@constant_folding.handler(VectorMatrixMultiply)
def _handle_vector_matrix_multiply(context, expression):
    vector = context.get(expression.loperand)
    matrix = context.get(expression.roperand)
    if isinstance(matrix, MatrixConstant) and isinstance(vector, VectorConstant):
        x, y, z = vector._values
        return VectorConstant(
            x*matrix.a00 + y*matrix.a10 + z*matrix.a20,
            x*matrix.a01 + y*matrix.a11 + z*matrix.a21,
            x*matrix.a02 + y*matrix.a12 + z*matrix.a22,
        )
    elif vector == VectorConstant(0, 0, 0) or matrix == Matrix.IDENTITY:
        return vector
    elif matrix == Matrix.ZERO:
        return VectorConstant(0, 0, 0)
    return VectorMatrixMultiply(vector, matrix)


@constant_folding.handler(MatrixMultiply)
def _handle_matrix_multiply(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    if isinstance(left, MatrixConstant) and isinstance(right, MatrixConstant):
        m1, m2 = left, right
        return MatrixConstant(
            m1.a00*m2.a00 + m1.a01*m2.a10 + m1.a02*m2.a20 + m1.a03*m2.a30,
            m1.a00*m2.a01 + m1.a01*m2.a11 + m1.a02*m2.a21 + m1.a03*m2.a31,
            m1.a00*m2.a02 + m1.a01*m2.a12 + m1.a02*m2.a22 + m1.a03*m2.a32,
            m1.a00*m2.a03 + m1.a01*m2.a13 + m1.a02*m2.a23 + m1.a03*m2.a33,
            m1.a10*m2.a00 + m1.a11*m2.a10 + m1.a12*m2.a20 + m1.a13*m2.a30,
            m1.a10*m2.a01 + m1.a11*m2.a11 + m1.a12*m2.a21 + m1.a13*m2.a31,
            m1.a10*m2.a02 + m1.a11*m2.a12 + m1.a12*m2.a22 + m1.a13*m2.a32,
            m1.a10*m2.a03 + m1.a11*m2.a13 + m1.a12*m2.a23 + m1.a13*m2.a33,
            m1.a20*m2.a00 + m1.a21*m2.a10 + m1.a22*m2.a20 + m1.a23*m2.a30,
            m1.a20*m2.a01 + m1.a21*m2.a11 + m1.a22*m2.a21 + m1.a23*m2.a31,
            m1.a20*m2.a02 + m1.a21*m2.a12 + m1.a22*m2.a22 + m1.a23*m2.a32,
            m1.a20*m2.a03 + m1.a21*m2.a13 + m1.a22*m2.a23 + m1.a23*m2.a33,
            m1.a30*m2.a00 + m1.a31*m2.a10 + m1.a32*m2.a20 + m1.a33*m2.a30,
            m1.a30*m2.a01 + m1.a31*m2.a11 + m1.a32*m2.a21 + m1.a33*m2.a31,
            m1.a30*m2.a02 + m1.a31*m2.a12 + m1.a32*m2.a22 + m1.a33*m2.a32,
            m1.a30*m2.a03 + m1.a31*m2.a13 + m1.a32*m2.a23 + m1.a33*m2.a33,
        )
    elif left == Matrix.IDENTITY or right == Matrix.ZERO:
        return right
    elif right == Matrix.IDENTITY or left == Matrix.ZERO:
        return left
    elif (
        (isinstance(left, MatrixInverse) and left.operand == right)
        or (isinstance(right, MatrixInverse) and right.operand == left)
    ):
        return Matrix.IDENTITY
    return MatrixMultiply(left, right)


@constant_folding.handler(MatrixTranspose)
def _handle_matrix_transpose(context, expression):
    operand = context.get(expression.operand)
    if isinstance(operand, MatrixConstant):
        return MatrixConstant(
            operand.a00, operand.a10, operand.a20, operand.a30,
            operand.a01, operand.a11, operand.a21, operand.a31,
            operand.a02, operand.a12, operand.a22, operand.a32,
            operand.a03, operand.a13, operand.a23, operand.a33,
        )
    if isinstance(operand, MatrixTranspose):
        return operand.operand
    return MatrixTranspose(operand)


@constant_folding.handler(MatrixInverse)
def _handle_matrix_inverse(context, expression):
    operand = context.get(expression.operand)
    if operand == Matrix.IDENTITY:
        return operand
    elif isinstance(operand, MatrixInverse):
        return operand.operand
    elif isinstance(operand, MatrixConstant):
        m = operand
        aa = (m.a11 * m.a22 * m.a33 - m.a11 * m.a23 * m.a32 -
              m.a21 * m.a12 * m.a33 + m.a21 * m.a13 * m.a32 +
              m.a31 * m.a12 * m.a23 - m.a31 * m.a13 * m.a22)
        ba = (-m.a10 * m.a22 * m.a33 + m.a10 * m.a23 * m.a32 +
              m.a20 * m.a12 * m.a33 - m.a20 * m.a13 * m.a32 -
              m.a30 * m.a12 * m.a23 + m.a30 * m.a13 * m.a22)
        ca = (m.a10 * m.a21 * m.a33 - m.a10 * m.a23 * m.a31 -
              m.a20 * m.a11 * m.a33 + m.a20 * m.a13 * m.a31 +
              m.a30 * m.a11 * m.a23 - m.a30 * m.a13 * m.a21)
        da = (-m.a10  * m.a21 * m.a32 + m.a10  * m.a22 * m.a31 +
              m.a20 * m.a11 * m.a32 - m.a20 * m.a12 * m.a31 -
              m.a30 * m.a11 * m.a22 + m.a30 * m.a12 * m.a21)
        ab = (-m.a01 * m.a22 * m.a33 + m.a01 * m.a23 * m.a32 +
              m.a21 * m.a02 * m.a33 - m.a21 * m.a03 * m.a32 -
              m.a31 * m.a02 * m.a23 + m.a31 * m.a03 * m.a22)
        bb = (m.a00 * m.a22 * m.a33 - m.a00 * m.a23 * m.a32 -
              m.a20 * m.a02 * m.a33 + m.a20 * m.a03 * m.a32 +
              m.a30 * m.a02 * m.a23 - m.a30 * m.a03 * m.a22)
        cb = (-m.a00  * m.a21 * m.a33 + m.a00 * m.a23 * m.a31 +
              m.a20 * m.a01 * m.a33 - m.a20 * m.a03 * m.a31 -
              m.a30 * m.a01 * m.a23 + m.a30 * m.a03 * m.a21)
        db = (m.a00 * m.a21 * m.a32 - m.a00 * m.a22 * m.a31 -
              m.a20 * m.a01 * m.a32 + m.a20 * m.a02 * m.a31 +
              m.a30 * m.a01 * m.a22 - m.a30 * m.a02 * m.a21)
        ac = (m.a01 * m.a12 * m.a33 - m.a01 * m.a13 * m.a32 -
              m.a11 * m.a02 * m.a33 + m.a11 * m.a03 * m.a32 +
              m.a31 * m.a02 * m.a13 - m.a31 * m.a03 * m.a12)
        bc = (-m.a00 * m.a12 * m.a33 + m.a00 * m.a13 * m.a32 +
              m.a10 * m.a02 * m.a33 - m.a10 * m.a03 * m.a32 -
              m.a30 * m.a02 * m.a13 + m.a30 * m.a03 * m.a12)
        cc = (m.a00 * m.a11 * m.a33 - m.a00 * m.a13 * m.a31 -
              m.a10 * m.a01 * m.a33 + m.a10 * m.a03 * m.a31 +
              m.a30 * m.a01 * m.a13 - m.a30 * m.a03 * m.a11)
        dc = (-m.a00 * m.a11 * m.a32 + m.a00 * m.a12 * m.a31 +
              m.a10 * m.a01 * m.a32 - m.a10 * m.a02 * m.a31 -
              m.a30 * m.a01 * m.a12 + m.a30 * m.a02 * m.a11)
        ad = (-m.a01 * m.a12 * m.a23 + m.a01 * m.a13 * m.a22 +
              m.a11 * m.a02 * m.a23 - m.a11 * m.a03 * m.a22 -
              m.a21 * m.a02 * m.a13 + m.a21 * m.a03 * m.a12)
        bd = (m.a00 * m.a12 * m.a23 - m.a00 * m.a13 * m.a22 -
              m.a10 * m.a02 * m.a23 + m.a10 * m.a03 * m.a22 +
              m.a20 * m.a02 * m.a13 - m.a20 * m.a03 * m.a12)
        cd = (-m.a00 * m.a11 * m.a23 + m.a00 * m.a13 * m.a21 +
              m.a10 * m.a01 * m.a23 - m.a10 * m.a03 * m.a21 -
              m.a20 * m.a01 * m.a13 + m.a20 * m.a03 * m.a11)
        dd = (m.a00 * m.a11 * m.a22 - m.a00 * m.a12 * m.a21 - 
              m.a10 * m.a01 * m.a22 + m.a10 * m.a02 * m.a21 + 
              m.a20 * m.a01 * m.a12 - m.a20 * m.a02 * m.a11)
        det = 1.0 / (m.a00 * aa + m.a01 * ba + m.a02 * ca + m.a03 * da)
        return MatrixConstant(
            aa * det, ab * det, ac * det, ad * det,
            ba * det, bb * det, bc * det, bd * det,
            ca * det, cb * det, cc * det, cd * det,
            da * det, db * det, dc * det, dd * det,
        )
    return MatrixInverse(operand)
