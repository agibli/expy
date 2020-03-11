from __future__ import division

from .expression import (
    Expression,
    Field,
    abstract_expression,
    unary_expression,
    binary_expression,
    cast_expression,
    expr,
)
from . import type_conversions


type_conversions.register_conversion(float, int)
type_conversions.register_conversion(float, bool)
type_conversions.register_conversion(int, float)
type_conversions.register_conversion(int, bool)
type_conversions.register_conversion(bool, float)
type_conversions.register_conversion(bool, int)


@abstract_expression
class Boolean(Expression):

    def __invert__(self):
        return BooleanInverse(self)

    def __and__(self, other):
        return BooleanAnd(self, other)

    def __rand__(self, other):
        return BooleanAnd(other, self)

    def __or__(self, other):
        return BooleanOr(self, other)

    def __ror__(self, other):
        return BooleanOr(other, self)


BooleanConstant = cast_expression("BooleanConstant", Boolean, bool)
BooleanInverse = unary_expression("BooleanInverse", Boolean)
BooleanAnd = binary_expression("BooleanAnd", Boolean)
BooleanOr = binary_expression("BooleanOr", Boolean)


@abstract_expression
class Integer(Expression):

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def __add__(self, other):
        other = expr(other)
        if isinstance(other, Scalar):
            return ScalarAdd(self, other)
        return IntegerAdd(self, other)

    def __radd__(self, other):
        return expr(other) + self

    def __sub__(self, other):
        other = expr(other)
        if isinstance(other, Scalar):
            return ScalarSubtract(self, other)
        return IntegerSubtract(self, other)

    def __rsub__(self, other):
        return expr(other) - self

    def __mul__(self, other):
        other = expr(other)
        if isinstance(other, Scalar):
            return ScalarMultiply(self, other)
        if isinstance(other, Vector):
            return VectorMultiply(other, self)
        return IntegerMultiply(self, other)

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return ScalarDivide(self, other)

    def __rtruediv__(self, other):
        return expr(other) / self

    def __pow__(self, other):
        other = expr(other)
        if isinstance(other, Scalar):
            return ScalarPower(self, other)
        return IntegerPower(self, other)

    def __rpow__(self, other):
        expr(other) ** self

    def __eq__(self, other):
        return IntegerEquals(self, other)

    def __ne__(self, other):
        return IntegerNotEquals(self, other)

    def __gt__(self, other):
        return IntegerGreaterThan(self, other)

    def __ge__(self, other):
        return IntegerGreaterThanEquals(self, other)

    def __lt__(self, other):
        return IntegerLessThan(self, other)

    def __le__(self, other):
        return IntegerLessThanEquals(self, other)


IntegerConstant = cast_expression("IntegerConstant", Integer, int)
IntegerAdd = binary_expression("IntegerAdd", Integer)
IntegerSubtract = binary_expression("IntegerSubtract", Integer)
IntegerMultiply = binary_expression("IntegerMultiply", Integer)
IntegerDivide = binary_expression("IntegerDivide", Integer)
IntegerPower = binary_expression("IntegerPower", Integer)
IntegerEquals = binary_expression("IntegerEquals", Boolean, Integer)
IntegerNotEquals = binary_expression("IntegerNotEquals", Boolean, Integer)
IntegerGreaterThan = binary_expression("IntegerGreaterThan", Boolean, Integer)
IntegerGreaterThanEquals = binary_expression("IntegerGreaterThanEquals", Boolean, Integer)
IntegerLessThan = binary_expression("IntegerLessThan", Boolean, Integer)
IntegerLessThanEquals = binary_expression("IntegerLessThanEquals", Boolean, Integer)


@abstract_expression
class Scalar(Expression):

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def __add__(self, other):
        return ScalarAdd(self, other)

    def __radd__(self, other):
        return expr(other) + self

    def __sub__(self, other):
        return ScalarSubtract(self, other)

    def __rsub__(self, other):
        return expr(other) - self

    def __mul__(self, other):
        other = expr(other)
        if isinstance(other, Vector):
            return VectorMultiply(other, self)
        return ScalarMultiply(self, other)

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return ScalarDivide(self, other)

    def __rtruediv__(self, other):
        return expr(other) / self

    def __pow__(self, other):
        return ScalarPower(self, other)

    def __rpow__(self, other):
        expr(other) ** self

    def __eq__(self, other):
        return ScalarEquals(self, other)

    def __ne__(self, other):
        return ScalarNotEquals(self, other)

    def __gt__(self, other):
        return ScalarGreaterThan(self, other)

    def __ge__(self, other):
        return ScalarGreaterThanEquals(self, other)

    def __lt__(self, other):
        return ScalarLessThan(self, other)

    def __le__(self, other):
        return ScalarLessThanEquals(self, other)


ScalarConstant = cast_expression("ScalarConstant", Scalar, float)
ScalarAdd = binary_expression("ScalarAdd", Scalar)
ScalarSubtract = binary_expression("ScalarSubtract", Scalar)
ScalarMultiply = binary_expression("ScalarMultiply", Scalar)
ScalarDivide = binary_expression("ScalarDivide", Scalar)
ScalarEquals = binary_expression("ScalarEquals", Boolean, Scalar)
ScalarNotEquals = binary_expression("ScalarNotEquals", Boolean, Scalar)
ScalarGreaterThan = binary_expression("ScalarGreaterThan", Boolean, Scalar)
ScalarGreaterThanEquals = binary_expression("ScalarGreaterThanEquals", Boolean, Scalar)
ScalarLessThan = binary_expression("ScalarLessThan", Boolean, Scalar)
ScalarLessThanEquals = binary_expression("ScalarLessThanEquals", Boolean, Scalar)

ScalarFromInteger = cast_expression("ScalarFromInteger", Scalar, Integer)
ScalarFromBoolean = cast_expression("ScalarFromBoolean", Scalar, Boolean)
IntegerFromScalar = cast_expression("IntegerFromScalar", Integer, Scalar)
IntegerFromBoolean = cast_expression("IntegerFromBoolean", Integer, Boolean)
BooleanFromScalar = cast_expression("BooleanFromScalar", Boolean, Scalar)
BooleanFromInteger = cast_expression("BooleanFromInteger", Boolean, Integer)


@abstract_expression
class Vector(Expression):

    def __neg__(self):
        return self * -1

    def __pos__(self):
        return self

    def __add__(self, other):
        return VectorAdd(other, self)

    def __sub__(self, other):
        return VectorSubtract(self, other)

    def __mul__(self, other):
        return VectorMultiply(self, other)

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return VectorDivide(self, other)

    def __xor__(self, other):
        return self.cross(other)

    @property
    def x(self):
        return VectorGetX(self)

    @property
    def y(self):
        return VectorGetY(self)

    @property
    def z(self):
        return VectorGetZ(self)

    def dot(self, other):
        return VectorDotProduct(self, other)

    def cross(self, other):
        return VectorCrossProduct(self, other)

    def length(self):
        return VectorLength(self)

    def normalized(self):
        return VectorNormalize(self)


class VectorConstant(Vector):
    xvalue = Field(float)
    yvalue = Field(float)
    zvalue = Field(float)


class VectorFromScalar(Vector):
    xvalue = Field(Scalar)
    yvalue = Field(Scalar)
    zvalue = Field(Scalar)


VectorGetX = unary_expression("VectorGetX", Scalar, Vector)
VectorGetY = unary_expression("VectorGetY", Scalar, Vector)
VectorGetZ = unary_expression("VectorGetZ", Scalar, Vector)
VectorAdd = binary_expression("VectorAdd", Vector)
VectorSubtract = binary_expression("VectorSubtract", Vector)
VectorMultiply = binary_expression("VectorMultiply", Vector, Vector, Scalar)
VectorDivide = binary_expression("VectorDivide", Vector, Vector, Scalar)
VectorDotProduct = binary_expression("VectorDotProduct", Vector, Scalar)
VectorCrossProduct = binary_expression("VectorCrossProduct", Vector)
VectorLength = unary_expression("VectorLength", Scalar, Vector)
VectorNormalize = unary_expression("VectorNormalize", Vector)
