from enum import Enum

from ..expression import (
    Expression,
    Field,
    abstract_expression,
    unary_expression,
    binary_expression,
    _expression_type,
)
from .transform import Transform
from .math import Boolean, Integer, Scalar, Vector, Matrix


@abstract_expression
class Scene(Expression):
    @property
    def root(self):
        return SceneRoot(self)


class DefaultScene(Scene): pass


Scene.DEFAULT = DefaultScene()


@abstract_expression
class Object(Expression):
    @property
    def parent(self):
        return ObjectParent(self)

    @property
    def scene(self):
        return ObjectScene(self)

    @property
    def local(self):
        return ObjectLocalTransform(self)

    @property
    def world(self):
        return ObjectWorldTransform(self)

    @property
    def find_child(self, name, recursive=False):
        return ObjectFindChild(self, name, recursive)


class SceneRoot(Object):
    scene = Field(Scene)


ObjectParent = unary_expression("ObjectParent", Object, Object)
ObjectScene = unary_expression("ObjectScene", Scene, Object)
ObjectLocalTransform = unary_expression("ObjectLocalTransform", Transform, Object)
ObjectWorldTransform = unary_expression("ObjectWorldTransform", Transform, Object)


class ObjectFindChild(Object):
    parent = Field(Object)
    name = Field(str)
    recursive = Field(bool, default=False)


class CreateObject(Object):
    name = Field(str)
    transform = Field(Transform, default=Transform.IDENTITY)
    parent = Field(Object, default=Scene.DEFAULT.root)


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
