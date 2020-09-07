from __future__ import division

from ..expression import (
    Expression,
    Field,
    abstract_expression,
    unary_expression,
    binary_expression,
    cast_expression,
    expr,
)
from .. import type_conversions


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

    def eq(self, other):
        return BooleanEquals(other, self)

    def ne(self, other):
        return BooleanNotEquals(other, self)


def boolean(value=False):
    return type_conversions.convert(Boolean, value)


BooleanConstant = cast_expression("BooleanConstant", Boolean, bool)
BooleanInverse = unary_expression("BooleanInverse", Boolean)
BooleanAnd = binary_expression("BooleanAnd", Boolean)
BooleanOr = binary_expression("BooleanOr", Boolean)
BooleanEquals = binary_expression("BooleanEquals", Boolean)
BooleanNotEquals = binary_expression("BooleanNotEquals", Boolean)


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
        elif isinstance(other, Matrix):
            return MatrixScalarMultiply(other, self)
        return IntegerMultiply(self, other)

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return ScalarDivide(self, other)

    def __rtruediv__(self, other):
        return expr(other) / self

    __div__ = __truediv__
    __rdiv__ = __rtruediv__

    def __pow__(self, other):
        return ScalarPower(self, other)

    def __rpow__(self, other):
        expr(other) ** self

    def eq(self, other):
        return IntegerEquals(self, other)

    def ne(self, other):
        return IntegerNotEquals(self, other)

    def __gt__(self, other):
        return IntegerGreaterThan(self, other)

    def __ge__(self, other):
        return IntegerGreaterThanEquals(self, other)

    def __lt__(self, other):
        return IntegerLessThan(self, other)

    def __le__(self, other):
        return IntegerLessThanEquals(self, other)


def integer(value=0):
    return type_conversions.convert(Integer, value)


IntegerConstant = cast_expression("IntegerConstant", Integer, int)

IntegerAdd = binary_expression("IntegerAdd", Integer)
IntegerSubtract = binary_expression("IntegerSubtract", Integer)
IntegerMultiply = binary_expression("IntegerMultiply", Integer)
IntegerDivide = binary_expression("IntegerDivide", Integer)
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
        elif isinstance(other, Matrix):
            return MatrixScalarMultiply(other, self)
        return ScalarMultiply(self, other)

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return ScalarDivide(self, other)

    def __rtruediv__(self, other):
        return expr(other) / self

    __div__ = __truediv__
    __rdiv__ = __rtruediv__

    def __pow__(self, other):
        return ScalarPower(self, other)

    def __rpow__(self, other):
        expr(other) ** self

    def eq(self, other):
        return ScalarEquals(self, other)

    def ne(self, other):
        return ScalarNotEquals(self, other)

    def __gt__(self, other):
        return ScalarGreaterThan(self, other)

    def __ge__(self, other):
        return ScalarGreaterThanEquals(self, other)

    def __lt__(self, other):
        return ScalarLessThan(self, other)

    def __le__(self, other):
        return ScalarLessThanEquals(self, other)


def scalar(value=0.0):
    return type_conversions.convert(Scalar, value)


ScalarConstant = cast_expression("ScalarConstant", Scalar, float)
ScalarAdd = binary_expression("ScalarAdd", Scalar)
ScalarSubtract = binary_expression("ScalarSubtract", Scalar)
ScalarMultiply = binary_expression("ScalarMultiply", Scalar)
ScalarDivide = binary_expression("ScalarDivide", Scalar)
ScalarPower = binary_expression("ScalarPower", Scalar)
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
        other = expr(other)
        if isinstance(other, Matrix):
            return VectorMatrixMultiply(self, other)
        return VectorMultiply(self, other)

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return VectorDivide(self, other)

    __div__ = __truediv__

    def __xor__(self, other):
        return self.cross(other)

    @property
    def x(self):
        return VectorComponent(self, 0)

    @property
    def y(self):
        return VectorComponent(self, 1)

    @property
    def z(self):
        return VectorComponent(self, 2)

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

    @property
    def x(self):
        return ScalarConstant(self.xvalue)

    @property
    def y(self):
        return ScalarConstant(self.yvalue)

    @property
    def z(self):
        return ScalarConstant(self.zvalue)


Vector.ZERO = VectorConstant(0.0, 0.0, 0.0)
Vector.X = VectorConstant(1.0, 0.0, 0.0)
Vector.Y = VectorConstant(0.0, 1.0, 0.0)
Vector.Z = VectorConstant(0.0, 0.0, 1.0)
Vector.ONES = VectorConstant(1.0, 1.0, 1.0)


def vector(*args):
    if len(args) == 0:
        return Vector.ZERO
    elif len(args) == 1:
        return type_conversions.convert(Vector, args[0])
    return type_conversions.convert(Vector, args)


@type_conversions.conversion(Scalar, tuple)
@type_conversions.conversion(Scalar, list)
def _vector_from_args(value):
    try:
        return VectorConstant(*value)
    except TypeError:
        return VectorFromScalar(*value)


class VectorComponent(Scalar):
    value = Field(Vector)
    index = Field(int)


class VectorFromScalar(Vector):
    x = Field(Scalar)
    y = Field(Scalar)
    z = Field(Scalar)


VectorAdd = binary_expression("VectorAdd", Vector)
VectorSubtract = binary_expression("VectorSubtract", Vector)
VectorMultiply = binary_expression("VectorMultiply", Vector, Vector, Scalar)
VectorDivide = binary_expression("VectorDivide", Vector, Vector, Scalar)
VectorDotProduct = binary_expression("VectorDotProduct", Scalar, Vector)
VectorCrossProduct = binary_expression("VectorCrossProduct", Vector)
VectorLength = unary_expression("VectorLength", Scalar, Vector)
VectorNormalize = unary_expression("VectorNormalize", Vector)


@abstract_expression
class Matrix(Expression):

    def __add__(self, other):
        return MatrixAdd(self, other)

    def __radd__(self, other):
        return expr(other) + self

    def __sub__(self, other):
        return MatrixSubtract(self, other)

    def __rsub__(self, other):
        return expr(other) - self

    def __mul__(self, other):
        other = expr(other)
        if isinstance(other, Matrix):
            return MatrixMultiply(self, other)
        elif isinstance(other, (Scalar, Integer)):
            return MatrixScalarMultiply(self, other)
        elif isinstance(other, Vector):
            return MatrixVectorMultiply(self, other)
        return NotImplemented

    def __rmul__(self, other):
        return expr(other) * self

    def __truediv__(self, other):
        return MatrixDivide(self, other)

    __div__ = __truediv__

    def __getitem__(self, ij):
        i, j = ij
        return MatrixComponent(self, i, j)

    def inverse(self):
        return MatrixInverse(self)

    def transpose(self):
        return MatrixTranspose(self)


class MatrixConstant(Matrix):
    a00 = Field(float, default=1.0)
    a01 = Field(float, default=0.0)
    a02 = Field(float, default=0.0)
    a03 = Field(float, default=0.0)
    a10 = Field(float, default=0.0)
    a11 = Field(float, default=1.0)
    a12 = Field(float, default=0.0)
    a13 = Field(float, default=0.0)
    a20 = Field(float, default=0.0)
    a21 = Field(float, default=0.0)
    a22 = Field(float, default=1.0)
    a23 = Field(float, default=0.0)
    a30 = Field(float, default=0.0)
    a31 = Field(float, default=0.0)
    a32 = Field(float, default=0.0)
    a33 = Field(float, default=1.0)

    def __getitem__(self, ij):
        return ScalarConstant(getattr(self, "a{}{}".format(*ij)))


Matrix.ZERO = MatrixConstant(0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0)
Matrix.IDENTITY = MatrixConstant(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)


def matrix(*args):
    if len(args) == 0:
        return Matrix.IDENTITY
    elif len(args) == 1:
        return type_conversions.convert(Matrix, args[0])
    return type_conversions.convert(Matrix, args)


@type_conversions.conversion(Matrix, tuple)
@type_conversions.conversion(Matrix, list)
def _matrix_from_args(value):
    if len(value) == 4:
        value = [value[i][j] for i in range(4) for j in range(4)]
    try:
        return MatrixConstant(*value)
    except TypeError:
        return MatrixFromScalar(*value)


class MatrixFromScalar(Matrix):
    a00 = Field(Scalar, default=1.0)
    a01 = Field(Scalar, default=0.0)
    a02 = Field(Scalar, default=0.0)
    a03 = Field(Scalar, default=0.0)
    a10 = Field(Scalar, default=0.0)
    a11 = Field(Scalar, default=1.0)
    a12 = Field(Scalar, default=0.0)
    a13 = Field(Scalar, default=0.0)
    a20 = Field(Scalar, default=0.0)
    a21 = Field(Scalar, default=0.0)
    a22 = Field(Scalar, default=1.0)
    a23 = Field(Scalar, default=0.0)
    a30 = Field(Scalar, default=0.0)
    a31 = Field(Scalar, default=0.0)
    a32 = Field(Scalar, default=0.0)
    a33 = Field(Scalar, default=1.0)

    def __getitem__(self, ij):
        return getattr(self, "a{}{}".format(*ij))


class MatrixComponent(Scalar):
    value = Field(Matrix)
    row = Field(int)
    column = Field(int)


MatrixInverse = unary_expression("MatrixInverse", Matrix)
MatrixTranspose = unary_expression("MatrixTranspose", Matrix)
MatrixAdd = binary_expression("MatrixAdd", Matrix)
MatrixSubtract = binary_expression("MatrixSubtract", Matrix)
MatrixMultiply = binary_expression("MatrixMultiply", Matrix)
MatrixScalarMultiply = binary_expression("MatrixScalarMultiply", Matrix, Matrix, Scalar)
MatrixDivide = binary_expression("MatrixDivide", Matrix, Matrix, Scalar)
VectorMatrixMultiply = binary_expression("VectorMatrixMultiply", Vector, Vector, Matrix)
MatrixVectorMultiply = binary_expression("MatrixVectorMultiply", Vector, Matrix, Vector)
