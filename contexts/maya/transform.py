import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expressions.transform import *

from .context import (
    maya_builder,
    ValueResult,
    AttributeResult,
    CompoundResult,
    TransformResult,
    MatrixTransformResult,
    EulerRotationResult,
)
from .expressions import (
    MayaBooleanAttribute,
    MayaIntegerAttribute,
    MayaScalarAttribute,
    MayaVectorAttribute,
    MayaMatrixAttribute,
)


_ROTATE_ORDERS = {
    RotateOrder.XYZ: 0,
    RotateOrder.YZX: 1,
    RotateOrder.ZXY: 2,
    RotateOrder.XZY: 3,
    RotateOrder.YXZ: 4,
    RotateOrder.ZYX: 5,
}


@maya_builder.handler(RotationIdentity)
def _handle_rotation_identity(context, expression):
    return EulerRotationResult(
        angles=ValueResult(dt.Vector(0,0,0)),
    )


@maya_builder.handler(EulerRotation)
def _handle_euler_rotation(context, expression):
    return EulerRotationResult(
        angles=CompoundResult(
            context.get(expression.x),
            context.get(expression.y),
            context.get(expression.z),
        ),
        order=ValueResult(_ROTATE_ORDERS[expression.order]),
    )


@maya_builder.handler(TransformIdentity)
def _handle_transform_identity(context, expression):
    return TransformResult(
        translation=ValueResult(dt.Point(0, 0, 0)),
        rotation=context.get(Rotation.IDENTITY),
        scale=ValueResult(dt.Vector(1, 1, 1)),
    )


@maya_builder.handler(ComposeTransform)
def _handle_compose_transform(context, expression):
    return TransformResult(
        translation=context.get(expression.translation),
        rotation=context.get(expression.rotation),
        scale=context.get(expression.scale),
    )


@maya_builder.handler(Transform.translation)
def _handle_transform_translation(context, expression):
    return context.get(expression.self).translation


@maya_builder.handler(Transform.rotation)
def _handle_transform_rotation(context, expression):
    return context.get(expression.self).rotation


@maya_builder.handler(Transform.scale)
def _handle_transform_scale(context, expression):
    return context.get(expression.self).scale


@maya_builder.handler(LocalToWorldTransform)
def _handle_local_to_world_transform(context, expression):
    transform = context.get(expression.transform)
    parent = context.get(expression.parent)
    try:
        return transform.to_world(parent)
    except NotImplementedError:
        return ctx.get(matrix(transform) * matrix(parent))


@maya_builder.handler(WorldToLocalTransform)
def _handle_world_to_local_transform(context, expression):
    transform = context.get(expression.transform)
    parent = context.get(expression.parent)
    try:
        return transform.to_world(parent)
    except NotImplementedError:
        return ctx.get(matrix(transform) * matrix(parent).inverse())


@maya_builder.handler(MatrixFromTransform)
def _handle_matrix_from_transform(context, expression):
    transform_result = context.get(expression.value)
    try:
        return transform_result.matrix
    except AttributeError:
        cmds.loadPlugin("matrixNodes", quiet=True)
        compose = pm.createNode("composeMatrix")
        transform_result.translation.assign(compose.inputTranslate)
        transform_result.rotation.assign_compose_matrix(compose)
        transform_result.scale.assign(compose.inputScale)
        return AttributeResult(compose.outputMatrix)


@maya_builder.handler(TransformFromMatrix)
def _handle_transform_from_matrix(context, expression):
    matrix_result = context.get(expression.value)
    try:
        return matrix_result.decompose
    except AttributeError:
        return MatrixTransformResult(matrix_result)
