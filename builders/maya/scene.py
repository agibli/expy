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


@maya_builder.handler(DefaultScene)
def _handle_default_scene(context, expression):
    return None


@maya_builder.handler(SceneRoot)
def _handle_scene_root(context, expression):
    return None


@maya_builder.handler(CreateObject)
def _handle_create_object(context, expression):
    parent = context.get(expression.parent)
    result = pm.createNode("transform", name=expression.name)
    if parent is not None:
        result.setParent(parent)
    context.get(expression.transform).assign_transform(result)
    return result


@maya_builder.handler(ObjectParent)
def _handle_object_parent(context, expression):
    obj = context.get(expression)
    if obj is None:
        return None
    return obj.getParent()


@maya_builder.handler(ObjectScene)
def _handle_object_scene(context, expression):
    return None


@maya_builder.handler(ObjectLocalTransform)
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
