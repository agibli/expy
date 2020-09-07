from enum import Enum

from ..expression import (
    Expression,
    Field,
    Output,
    SelfType,
    abstract_expression,
    unary_expression,
    binary_expression,
    _expression_type,
)
from .transform import Transform
from .math import Boolean, Integer, Scalar, Vector, Matrix


@abstract_expression
class Object(Expression):
    parent = Output(SelfType)
    local = Output(Transform)
    world = Output(Transform)

    @property
    def find_child(self, name, recursive=False):
        return ObjectFindChild(self, name, recursive)


class RootObject(Object): pass


Object.ROOT = RootObject()


class ObjectFindChild(Object):
    parent = Field(Object)
    name = Field(str)
    recursive = Field(bool, default=False)


class CreateObject(Object):
    name = Field(str)
    transform = Field(Transform, default=Transform.IDENTITY)
    parent = Field(Object, default=Object.ROOT)


class CreateJoint(CreateObject):
    orient = Field(Rotation, default=Rotation.IDENTITY)
    display_scale = Field(Scalar, default=1.0)


def attribute_expression(name, attribute_type):
    class_namespace = {
        "name": Field(str),
        "object": Field(Object),
    }
    return _expression_type(name, attribute_type, class_namespace)


BooleanAttribute = attribute_expression("BooleanAttribute", Boolean)
IntegerAttribute = attribute_expression("IntegerAttribute", Integer)
ScalarAttribute = attribute_expression("ScalarAttribute", Scalar)
VectorAttribute = attribute_expression("VectorAttribute", Vector)
