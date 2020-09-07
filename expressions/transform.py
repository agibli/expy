from __future__ import absolute_import

from enum import Enum

from ..expression import (
    Expression,
    Field,
    abstract_expression,
    unary_expression,
    binary_expression,
    cast_expression,
)
from .math import (
    Scalar,
    ScalarConstant,
    Vector,
    VectorConstant,
    Matrix,
    MatrixConstant,
)


class Axis(Enum):
    X = "X"
    Y = "Y"
    Z = "Z"


class RotateOrder(Enum):
    XYZ = "XYZ"
    YXZ = "YXZ"
    XZY = "XZY"
    ZYX = "ZYX"
    YZX = "YZX"
    ZXY = "ZXY"


@abstract_expression
class Rotation(Expression):
    def to_euler(self, order=RotateOrder.XYZ):
        return EulerFromRotation(self, order)


class RotationIdentity(Rotation): pass
Rotation.IDENTITY = RotationIdentity()


class EulerRotation(Rotation):
    x = Field(Scalar, default=0.0)
    y = Field(Scalar, default=0.0)
    z = Field(Scalar, default=0.0)
    order = Field(RotateOrder, default=RotateOrder.XYZ)


@abstract_expression
class Transform(Expression):
    translation = Output(Vector)
    rotation = Output(Rotation)
    scale = Output(Vector)

    def local_to_world(self, parent):
        return LocalToWorldTransform(parent, self)

    def world_to_local(self, parent):
        return WorldToLocalTransform(parent, self)


class WorldToLocalTransform(Transform):
    parent = Field(Transform)
    transform = Field(Transform)


class LocalToWorldTransform(Transform):
    parent = Field(Transform)
    transform = Field(Transform)


class TransformIdentity(Transform):
    translation = Vector.ZERO
    rotation = Rotation.IDENTITY
    scale = Vector.ONES
Transform.IDENTITY = TransformIdentity()


class ComposeTransform(Transform):
    translation = Field(Vector, default=Vector.ZERO)
    rotation = Field(Rotation, default=Rotation.IDENTITY)
    scale = Field(Vector, default=Vector.ONES)


TransformFromMatrix = cast_expression("TransformFromMatrix", Transform, Matrix)
MatrixFromTransform = cast_expression("MatrixFromTransform", Matrix, Transform)
