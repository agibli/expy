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


def _decompose_translation(m):
    translation = VectorConstant(m.a30, m.a31, m.a32)
    linear = MatrixConstant(
        m.a00, m.a01, m.a02, 0,
        m.a10, m.a11, m.a12, 0,
        m.a20, m.a21, m.a22, 0,
        0, 0, 0, 1,
    )
    return translation, linear


def _unskew(m):
    ctx = ConstantFoldingContext()
    i = VectorConstant(m.a00, m.a01, m.a02)
    j = VectorConstant(m.a10, m.a11, m.a12)
    k = VectorConstant(m.a20, m.a21, m.a22)

    j_proj_i = ctx.get(i * j.dot(i) / i.dot(i))
    j_ortho = ctx.get(j - j_proj_i)

    k_proj_i = ctx.get(i * k.dot(i) / i.dot(i))
    k_ortho_i = ctx.get(k - k_proj_i)

    k_proj_j = ctx.get(j_ortho * k_ortho_i.dot(j_ortho) / j_ortho.dot(j_ortho))
    k_ortho = ctx.get(k_ortho_i - k_proj_j)

    return MatrixConstant(
        i.xvalue, i.yvalue, i.zvalue, 0,
        j_ortho.xvalue, j_ortho.yvalue, j_ortho.zvalue, 0,
        k_ortho.xvalue, k_ortho.yvalue, k_ortho.zvalue, 0,
        m.a30, m.a31, m.a32, 1,
    )


def _decompose_scale(m):
    i = VectorConstant(m.a00, m.a01, m.a02)
    j = VectorConstant(m.a10, m.a11, m.a12)
    k = VectorConstant(m.a20, m.a21, m.a22)
    det = (
        m.a00 * m.a11 * m.a22 - m.a00 * m.a12 * m.a21
        - m.a01 * m.a10 * m.a22 + m.a01 * m.a12 * m.a20
        + m.a02 * m.a10 * m.a21 - m.a02 * m.a11 * m.a20
    )
    sign = 1 if det >= 0 else -1

    scale = VectorConstant(
        math.sqrt(m.a00 * m.a00 + m.a01 * m.a01 + m.a02 * m.a02),
        math.sqrt(m.a10 * m.a10 + m.a11 * m.a11 + m.a12 * m.a12),
        math.sqrt(m.a20 * m.a20 + m.a21 * m.a21 + m.a22 * m.a22) * sign,
    )

    x_inv = 1.0 / scale.xvalue if scale.xvalue else 1.0
    y_inv = 1.0 / scale.yvalue if scale.yvalue else 1.0
    z_inv = 1.0 / scale.zvalue if scale.zvalue else 1.0

    unit = MatrixConstant(
        m.a00 * x_inv, m.a01 * x_inv, m.a02 * x_inv, 0.0,
        m.a10 * y_inv, m.a11 * y_inv, m.a12 * y_inv, 0.0,
        m.a20 * z_inv, m.a21 * z_inv, m.a22 * z_inv, 0.0,
        m.a30, m.a31, m.a32, 1.0,
    )
    return scale, unit


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
    transform = context.get(expression.self)
    if (
        isinstance(transform, TransformFromMatrix)
        and isinstance(transform.value, MatrixConstant)
    ):
        translation, rest = _decompose_translation(transform.value)
        return translation
    return transform.translation


@constant_folding.handler(Transform.rotation)
def _handle_transform_rotation(context, expression):
    return context.get(expression.self).rotation


@constant_folding.handler(Transform.scale)
def _handle_transform_scale(context, expression):
    transform = context.get(expression.self)
    if (
        isinstance(transform, TransformFromMatrix)
        and isinstance(transform.value, MatrixConstant)
    ):
        scale, rest = _decompose_scale(_unskew(transform.value))
        return scale
    return context.get(expression.self).scale


@constant_folding.handler(LocalToWorldTransform)
def _handle_local_to_world_transform(context, expression):
    local = context.get(expression.transform)
    parent = context.get(expression.parent)
    if local == Transform.IDENTITY:
        return parent
    if parent == Transform.IDENTITY:
        return local
    if isinstance(local, WorldToLocalTransform) and local.parent == parent:
        return local.transform
    return LocalToWorldTransform(transform=local, parent=parent)


@constant_folding.handler(WorldToLocalTransform)
def _handle_world_to_local_transform(context, expression):
    world = context.get(expression.transform)
    parent = context.get(expression.parent)
    if world == Transform.IDENTITY:
        return parent
    if parent == Transform.IDENTITY:
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
