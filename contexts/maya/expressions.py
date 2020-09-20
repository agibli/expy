from __future__ import absolute_import

import six

import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expression import (
    Expression,
    Field,
    abstract_expression,
    cast_expression,
    expr,
)
from ...expressions.math import (
    Boolean,
    BooleanConstant,
    Integer,
    IntegerConstant,
    Scalar,
    ScalarConstant,
    Vector,
    VectorConstant,
    Matrix,
    MatrixConstant,
)
from ...expressions.scene import Object
from ... import type_conversions


BOOLEAN_ATTR_TYPES = ("bool",)
INTEGER_ATTR_TYPES = ("bool", "char", "short", "long", "enum")
SCALAR_ATTR_TYPES = ("float", "double", "doubleAngle", "doubleLinear")
VECTOR_ATTR_TYPES = ("short3", "long3", "float3", "double3")
MATRIX_ATTR_TYPES = ("matrix",)
POINT_ATTRS = {
    nt.Transform: (
        "translate",
        "rotatePivot",
        "rotatePivotTranslate",
        "scalePivot",
        "scalePivotTranslate",
    ),
}


class MayaAttributeTypeHook(object):

    def __init__(self):
        self._attr_types = {}

    def register_type(self, name, attr_types, predicate=None):
        tag_type = type(name, (), {})
        if isinstance(attr_types, six.string_types):
            attr_types = (attr_types,)
        for attr_type in attr_types:
            attr_type_entries = self._attr_types.setdefault(attr_type, [])
            attr_type_entries.append((tag_type, predicate))
        return tag_type

    def __call__(self, attr):
        attr_type = attr.get(type=True)
        for tag_type, predicate in self._attr_types.get(attr_type, []):
            if not predicate or predicate(attr):
                return tag_type
        return type(attr)


_type_hook = MayaAttributeTypeHook()
type_conversions.register_type_hook(pm.Attribute, _type_hook)


def _predicate_from_attr_map(attrs_by_node_type):
    def predicate(attr):
        for node_type, attr_names in attrs_by_node_type.items():
            if (isinstance(attr.node(), node_type) and
                    attr.attrName(longName=True) in attr_names):
                return True
        return False
    return predicate

is_point_attr = _predicate_from_attr_map(POINT_ATTRS)


def maya_attr_expression(name, value_type, attr_types, predicate=None):
    tag_name = "_{}Tag".format(name)
    tag_type = _type_hook.register_type(tag_name, attr_types, predicate=predicate)
    result = cast_expression(name, value_type, tag_type)
    type_conversions.register_conversion(pm.Attribute, result)
    return result


MayaBooleanAttribute = maya_attr_expression(
    "MayaBooleanAttribute", Boolean, BOOLEAN_ATTR_TYPES,
)
MayaIntegerAttribute = maya_attr_expression(
    "MayaIntegerAttribute", Integer, INTEGER_ATTR_TYPES,
)
MayaScalarAttribute = maya_attr_expression(
    "MayaScalarAttribute", Scalar, SCALAR_ATTR_TYPES,
)
MayaVectorAttribute = maya_attr_expression(
    "MayaVectorAttribute", Vector, VECTOR_ATTR_TYPES,
)
MayaMatrixAttribute = maya_attr_expression(
    "MayaMatrixAttribute", Matrix, MATRIX_ATTR_TYPES,
)


@type_conversions.conversion(VectorConstant, dt.Point)
@type_conversions.conversion(VectorConstant, dt.Vector)
def _convert_vector_constant(value):
    return VectorConstant(*value)


@type_conversions.conversion(dt.Vector, VectorConstant)
def _convert_vector_constant(value):
    return dt.Vector(value.xvalue, value.yvalue, value.zvalue)


@type_conversions.conversion(dt.Point, VectorConstant)
def _convert_vector_constant(value):
    return dt.Point(value.xvalue, value.yvalue, value.zvalue)


@type_conversions.conversion(MatrixConstant, dt.Matrix)
def _convert_vector_constant(value):
    return MatrixConstant(*(a for row in value for a in row))


class MayaObject(Object):
    value = Field(nt.Transform)

    @property
    def parent(self):
        parent = self.value.getParent()
        if not parent:
            return Object.ROOT
        return MayaObject(parent)


type_conversions.register_conversion(MayaObject, nt.Transform)
type_conversions.register_conversion(nt.Transform, MayaObject, lambda c: c.value)
