import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expressions.scene import *
from ...expressions.transform import *

from .builder import (
    maya_builder,
    ValueResult,
    AttributeResult,
    CompoundResult,
    TransformResult,
    EulerRotationResult,
)


@maya_builder.handler(RootObject)
def _handle_root_object(context, expression):
    return None


@maya_builder.handler(CreateObject)
def _handle_create_object(context, expression):
    parent = context.get(expression.parent)
    result = pm.createNode("transform", name=expression.name)
    if parent is not None:
        result.setParent(parent)
    context.get(expression.transform).assign_transform(result)
    return result


@maya_builder.handler(Object.parent)
def _handle_object_parent(context, expression):
    obj = context.get(expression)
    if obj is None:
        return None
    return obj.getParent()


@maya_builder.handler(Object.local)
def _handle_object_local_transform(context, expression):
    obj = context.get(expression.operand)
    if obj is None:
        return context.get(Transform.IDENTITY)
    return TransformResult(
        translation=AttributeResult(obj.translate),
        rotation=EulerRotationResult(
            angles=AttributeResult(obj.rotate),
            order=AttributeResult(obj.rotateOrder),
        ),
        scale=AttributeResult(obj.scale),
    )
