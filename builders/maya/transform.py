import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expressions.transform import *

from .builder import (
    maya_builder,
    ValueResult,
    AttributeResult,
    CompoundResult,
    TransformResult,
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


@maya_builder.handler(TransformTranslation)
def _handle_transform_translation(context, expression):
    return context.get(expression.operand).translation


@maya_builder.handler(TransformRotation)
def _handle_transform_rotation(context, expression):
    return context.get(expression.operand).rotation


@maya_builder.handler(TransformScale)
def _handle_transform_scale(context, expression):
    return context.get(expression.operand).scale

