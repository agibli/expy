import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expressions.transform import *
from ...expressions.geometry import *

from .builder import (
    maya_builder,
    AttributeResult,
)


@maya_builder.handler(Circle)
def _handle_circle(context, expression):
    result = pm.createNode("makeNurbCircle")
    context.get(expression.radius).assign(result.radius)
    context.get(expression.normal).assign(result.normal)
    # attribute name conflicts with MakeNurbCircle.center() method
    context.get(expression.position).assign(result.attr("center"))
    return AttributeResult(result.outputCurve)


@maya_builder.handler(CurveInstance)
def _handle_curve_instance(context, expression):
    parent = context.get(expression.parent)
    if not parent:
        raise ValueError("Cannot instance curve under scene root")
    shape_name = parent.nodeName() + "Shape"
    result = pm.createNode("nurbsCurve", name=shape_name, parent=parent)
    context.get(expression.curve).assign(result.create)
    return result


@maya_builder.handler(CurveInstance.world_curve)
def _handle_curve_instance(context, expression):
    shape = context.get(expression.operand)
    return AttributeResult(shape.worldSpace[0])
