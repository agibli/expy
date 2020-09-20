from __future__ import absolute_import, division

import math
import operator
import functools

from ...expressions.math import Vector, ScalarConstant
from ...expressions.transform import *
from .context import constant_folding, ConstantFoldingContext


def _translation_matrix(x, y, z):
    return MatrixConstant(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        x, y, z, 1,
    )


def _is_constant_rotation(expression):
    if isinstance(expression, RotationIdentity):
        return True
    if (
        isinstance(expression, EulerRotation)
        and isinstance(expression.x, ScalarConstant)
        and isinstance(expression.y, ScalarConstant)
        and isinstance(expression.z, ScalarConstant)
    ):
        return True
    return False


def _x_rotation_matrix(deg):
    if not deg:
        return Matrix.IDENTITY
    rad = math.radians(deg)
    cos = math.cos(rad)
    sin = math.sin(rad)
    return MatrixConstant(
        1, 0, 0, 0,
        0, cos, sin, 0,
        0, -sin, cos, 0,
        0, 0, 0, 1,
    )


def _y_rotation_matrix(deg):
    if not deg:
        return Matrix.IDENTITY
    rad = math.radians(deg)
    cos = math.cos(rad)
    sin = math.sin(rad)
    return MatrixConstant(
        cos, 0, -sin, 0,
        0, 1, 0, 0,
        sin, 0, cos, 0,
        0, 0, 0, 1,
    )


def _z_rotation_matrix(deg):
    if not deg:
        return Matrix.IDENTITY
    rad = math.radians(deg)
    cos = math.cos(rad)
    sin = math.sin(rad)
    return MatrixConstant(
        cos, sin, 0, 0,
        -sin, cos, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    )


def _euler_rotation_matrix(x, y, z, order):
    X = _x_rotation_matrix(x)
    Y = _y_rotation_matrix(y)
    Z = _z_rotation_matrix(z)
    R1, R2, R3 = RotateOrder.sort(X, Y, Z, order)
    return ConstantFoldingContext().get(R1 * R2 * R3)


def _rotation_matrix(rotation):
    if isinstance(rotation, RotationIdentity):
        return Matrix.IDENTITY
    if isinstance(rotation, EulerRotation):
        return _euler_rotation_matrix(
            rotation.x.value,
            rotation.y.value,
            rotation.z.value,
            rotation.order,
        )
    raise NotImplementedError("Unsupported rotation constant: {}".format(rotation))


def _scale_matrix(x, y, z):
    return MatrixConstant(
        x, 0, 0, 0,
        0, y, 0, 0,
        0, 0, z, 0,
        0, 0, 0, 1,
    )


@constant_folding.handler(EulerRotation)
def _handle_euler_rotation(context, expression):
    x = context.get(expression.x)
    y = context.get(expression.y)
    z = context.get(expression.z)
    if (
        x == ScalarConstant(0)
        and y == ScalarConstant(0)
        and z == ScalarConstant(0)
    ):
        return Rotation.IDENTITY
    return EulerRotation(x, y, z, expression.order)


@constant_folding.handler(Transform.translation)
def _handle_transform_translation(context, expression):
    return context.get(expression.self).translation


@constant_folding.handler(Transform.rotation)
def _handle_transform_rotation(context, expression):
    return context.get(expression.self).rotation


@constant_folding.handler(Transform.scale)
def _handle_transform_scale(context, expression):
    return context.get(expression.self).scale


@constant_folding.handler(LocalToWorldTransform)
def _handle_local_to_world_transform(context, expression):
    local = context.get(expression.transform)
    parent = context.get(expression.parent)
    if local == Matrix.IDENTITY:
        return parent
    if parent == Matrix.IDENTITY:
        return local
    if isinstance(local, WorldToLocalTransform) and local.parent == parent:
        return local.transform
    return LocalToWorldTransform(transform=local, parent=parent)


@constant_folding.handler(WorldToLocalTransform)
def _handle_world_to_local_transform(context, expression):
    world = context.get(expression.transform)
    parent = context.get(expression.parent)
    if world == Matrix.IDENTITY:
        return parent
    if parent == Matrix.IDENTITY:
        return world
    if isinstance(world, LocalToWorldTransform) and world.parent == parent:
        return world.transform
    return WorldToLocalTransform(transform=world, parent=parent)


@constant_folding.handler(ComposeTransform)
def _handle_compose_transform(context, expression):
    translation = context.get(expression.translation)
    rotation = context.get(expression.rotation)
    scale = context.get(expression.scale)
    if (
        translation == Vector.ZERO
        and rotation == Rotation.IDENTITY
        and scale == Vector.ONES
    ):
        return Transform.IDENTITY
    return ComposeTransform(translation, rotation, scale)


@constant_folding.handler(TransformFromMatrix)
def _handle_transform_from_matrix(context, expression):
    matrix = context.get(expression.value)
    if matrix == Matrix.IDENTITY:
        return Transform.IDENTITY
    if isinstance(matrix, MatrixFromTransform):
        return matrix.value
    return TransformFromMatrix(matrix)


@constant_folding.handler(MatrixFromTransform)
def _handle_matrix_from_transform(context, expression):
    transform = context.get(expression.value)
    if transform == Transform.IDENTITY:
        return Matrix.IDENTITY
    if isinstance(transform, TransformFromMatrix):
        return transform.value
    if (
        isinstance(transform, ComposeTransform)
        and isinstance(transform.translation, VectorConstant)
        and isinstance(transform.scale, VectorConstant)
        and _is_constant_rotation(transform.rotation)
    ):
        translation = transform.translation
        rotation = transform.rotation
        scale = transform.scale
        try:
            T = _translation_matrix(translation.x, translation.y, translation.z)
            R = _rotation_matrix(rotation)
            S = _scale_matrix(scale.x, scale.y, scale.z)
            return ConstantFoldingContext().get(S * R * T)
        except NotImplementedError:
            # Unsupported rotation constant
            pass
    return MatrixFromTransform(transform)
