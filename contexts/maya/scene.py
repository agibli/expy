import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expressions.scene import *
from ...expressions.transform import *

from .expressions import MayaObject
from .context import (
    maya_builder,
    ValueResult,
    AttributeResult,
    WorldMatrixAttributeResult,
    CompoundResult,
    TransformResult,
    ObjectLocalTransformResult,
    MatrixTransformResult,
    EulerRotationResult,
)


@maya_builder.handler(MayaObject)
def _handle_maya_object(context, expression):
    return expression.value


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
    obj = context.get(expression.self)
    if obj is None:
        return None
    return obj.getParent()


@maya_builder.handler(Object.local)
def _handle_object_local_transform(context, expression):
    obj = context.get(expression.self)
    if obj is None:
        return context.get(Transform.IDENTITY)
    return ObjectLocalTransformResult(obj)


@maya_builder.handler(Object.world)
def _handle_object_world_transform(context, expression):
    obj = context.get(expression.self)
    if obj is None:
        return context.get(Transform.IDENTITY)
    return ObjectWorldTransformResult(obj)
