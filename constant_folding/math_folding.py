import math
import operator
import functools

from ..math_types import *
from .builder import constant_folding


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


@constant_folding.handler(BooleanAnd, propagate=False)
def _handle_boolean_and(context, expression):
    left = context.get(expression.loperand)
    is_left_constant = isinstance(left, BooleanConstant)
    if is_left_constant and not left.value:
        return BooleanConstant(False)
    right = context.get(expression.roperand)
    is_right_constant = isinstance(right, BooleanConstant)
    if is_left_constant and is_right_constant:
        return BooleanConstant(left.value and right.value)
    elif is_right_constant and not right.value:
        return BooleanConstant(False)
    return BooleanAnd(left, right)


@constant_folding.handler(BooleanOr, propagate=False)
def _handle_boolean_or(context, expression):
    left = context.get(expression.loperand)
    is_left_constant = isinstance(left, BooleanConstant)
    if is_left_constant and left.value:
        return BooleanConstant(True)
    right = context.get(expression.roperand)
    is_right_constant = isinstance(right, BooleanConstant)
    if is_left_constant and is_right_constant:
        return BooleanConstant(left.value or right.value)
    elif is_right_constant and right.value:
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
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return constant_type(left.value + right.value)
    elif is_left_constant and left.value == 0:
        # Identity: 0 + a = a
        return right
    elif is_right_constant and right.value == 0:
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
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return constant_type(left.value - right.value)
    elif is_right_constant and right.value == 0:
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
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return constant_type(left.value * right.value)
    elif is_left_constant and left.value == 1:
        # Identity: 1 * a = a
        return right
    elif is_right_constant and right.value == 1:
        # Identity: a * 1 = a
        return left
    elif is_left_constant and left.value == 0:
        # Identity: 0 * a = 0
        return left
    elif is_right_constant and right.value == 0:
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
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return constant_type(left.value / right.value)
    elif is_right_constant and right.value == 1:
        # Identity: a / 1 = a
        return left
    elif is_left_constant and left.value == 0:
        # Identity: 0 / a = 0 (a != 0)
        return left
    elif is_right_constant and right.value == 0:
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
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return constant_type(left.value ** right.value)
    elif is_right_constant and right.value == 1:
        # Identity: a ** 1 = a
        return left
    elif is_right_constant and right.value == 0:
        # Identity: a ** 0 = 1
        return constant_type(1)
    elif is_left_constant and left.value == 1:
        # Identity: 1 ** a = 1
        return left
    return type(expression)(left, right)

constant_folding.register_handler(
    ScalarPower, functools.partial(_handle_power, ScalarConstant)
)


def _handle_equals(constant_type, func, context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return BooleanConstant(func(left.value, right.value))
    elif left  == right:
        # Identity: a ** 1 = a
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
    is_left_constant = isinstance(left, constant_type)
    is_right_constant = isinstance(right, constant_type)
    if is_left_constant and is_right_constant:
        return BooleanConstant(func(left.value, right.value))
    elif left  == right:
        # Identity: a ** 1 = a
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
    x = context.get(expression.xvalue)
    y = context.get(expression.yvalue)
    z = context.get(expression.zvalue)
    if (
        isinstance(x, ScalarConstant)
        and isinstance(y, ScalarConstant)
        and isinstance(z, ScalarConstant)
    ):
        return VectorConstant(x, y, z)
    return VectorFromScalar(x, y, z)


def _is_constant_vector(vector, x, y, z):
    return (
        isinstance(vector, VectorConstant)
        and vector.xvalue == x
        and vector.yvalue == y
        and vector.zvalue == z
    )

_is_zero_vector = lambda v: _is_constant_vector(v, 0, 0, 0)
_is_one_vector = lambda v: _is_constant_vector(v, 1, 1, 1)
_is_x_vector = lambda v: _is_constant_vector(v, 1, 0, 0)
_is_y_vector = lambda v: _is_constant_vector(v, 0, 1, 0)
_is_z_vector = lambda v: _is_constant_vector(v, 0, 0, 1)


@constant_folding.handler(VectorAdd)
def _handle_vector_add(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    is_left_constant = isinstance(left, VectorConstant)
    is_right_constant = isinstance(right, VectorConstant)
    if is_left_constant and is_right_constant:
        return VectorConstant(
            left.xvalue + right.xvalue,
            left.yvalue + right.yvalue,
            left.zvalue + right.zvalue,
        )
    elif _is_zero_vector(left):
        return right
    elif _is_zero_vector(right):
        return left
    return VectorAdd(left, right)


@constant_folding.handler(VectorSubtract)
def _handle_vector_subtract(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    is_left_constant = isinstance(left, VectorConstant)
    is_right_constant = isinstance(right, VectorConstant)
    if is_left_constant and is_right_constant:
        return VectorConstant(
            left.xvalue - right.xvalue,
            left.yvalue - right.yvalue,
            left.zvalue - right.zvalue,
        )
    elif _is_zero_vector(right):
        return left
    return VectorSubtract(left, right)


@constant_folding.handler(VectorMultiply)
def _handle_vector_multiply(context, expression):
    vector = context.get(expression.loperand)
    scalar = context.get(expression.roperand)
    is_vector_constant = isinstance(vector, VectorConstant)
    is_scalar_constant = isinstance(scalar, ScalarConstant)
    if is_vector_constant and is_scalar_constant:
        return VectorConstant(
            vector.xvalue * scalar.value,
            vector.yvalue * scalar.value,
            vector.zvalue * scalar.value,
        )
    elif is_scalar_constant and scalar.value == 1:
        return vector
    elif is_scalar_constant and scalar.value == 0:
        return VectorConstant(0, 0, 0)
    elif _is_zero_vector(vector):
        return VectorConstant(0, 0, 0)
    return VectorMultiply(vector, scalar)


@constant_folding.handler(VectorDivide)
def _handle_vector_divide(context, expression):
    vector = context.get(expression.loperand)
    scalar = context.get(expression.roperand)
    is_vector_constant = isinstance(vector, VectorConstant)
    is_scalar_constant = isinstance(scalar, ScalarConstant)
    if is_vector_constant and is_scalar_constant:
        return VectorConstant(
            vector.xvalue / scalar.value,
            vector.yvalue / scalar.value,
            vector.zvalue / scalar.value,
        )
    elif is_scalar_constant and scalar.value == 1:
        return vector
    elif is_scalar_constant and scalar.value == 0:
        raise ZeroDivisionError
    elif _is_zero_vector(vector):
        return VectorConstant(0, 0, 0)
    return VectorDivide(vector, scalar)


@constant_folding.handler(VectorDotProduct)
def _handle_dot_product(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    is_left_constant = isinstance(left, VectorConstant)
    is_right_constant = isinstance(right, VectorConstant)
    if is_left_constant and is_right_constant:
        return ScalarConstant(
            left.xvalue * right.xvalue
            + left.yvalue * right.yvalue
            + left.zvalue * right.zvalue
        )
    elif _is_zero_vector(left) or _is_zero_vector(right):
        return ScalarConstant(0)
    for a, b in ((left, right), (right, left)):
        if _is_x_vector(a) and isinstance(b, VectorFromScalar):
            # Identity: (1,0,0)*(x,y,z) = x
            return b.xvalue
        elif _is_y_vector(a) and isinstance(b, VectorFromScalar):
            # Identity: (0,1,0)*(x,y,z) = y
            return b.yvalue
        elif _is_z_vector(a) and isinstance(b, VectorFromScalar):
            # Identity: (0,0,1)*(x,y,z) = z
            return b.zvalue
    return VectorDotProduct(left, right)


@constant_folding.handler(VectorCrossProduct)
def _handle_cross_product(context, expression):
    left = context.get(expression.loperand)
    right = context.get(expression.roperand)
    is_left_constant = isinstance(left, VectorConstant)
    is_right_constant = isinstance(right, VectorConstant)
    if is_left_constant and is_right_constant:
        return VectorConstant(
            left.yvalue * right.zvalue - left.zvalue * right.yvalue,
            left.zvalue * right.xvalue - left.xvalue * right.zvalue,
            left.xvalue * right.yvalue - left.yvalue * right.xvalue,
        )
    elif left == right or _is_zero_vector(left) or _is_zero_vector(right):
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
