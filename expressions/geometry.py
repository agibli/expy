from enum import Enum

from ..expression import (
    Expression,
    Field,
    abstract_expression,
    unary_expression,
    binary_expression,
    cast_expression,
)
from .math import Boolean, Integer, Scalar, Vector, Matrix
from .transform import Transform
from .scene import Object


class Geometry(Expression): pass


class Curve(Geometry):
    def point(self, u):
        return PointOnCurve(self, u)


class PointOnCurve(Expression):
    curve = Field(Curve)
    u = Field(Scalar)

    @property
    def position(self):
        return PointOnCurvePosition(self)

    @property
    def tangent(self):
        return PointOnCurveTangent(self)

    @property
    def normal(self):
        return PointOnCurveNormal(self)


PointOnCurvePosition = cast_expression("PointOnCurvePosition", Vector, PointOnCurve)
PointOnCurveTangent = unary_expression("PointOnCurveTangent", Vector, PointOnCurve)
PointOnCurveNormal = unary_expression("PointOnCurveNormal", Vector, PointOnCurve)

TransformCurve = binary_expression("TransformCurve", Curve, Transform, Curve)


class Surface(Geometry):
    def point(self, u, v):
        return PointOnSurface(self, u, v)


class PointOnSurface(Expression):
    surface = Field(Curve)
    u = Field(Scalar)
    v = Field(Scalar)

    @property
    def position(self):
        return PointOnSurfacePosition(self)

    @property
    def tangent_u(self):
        return PointOnSurfaceTangentU(self)

    @property
    def tangent_v(self):
        return PointOnSurfaceTangentV(self)

    @property
    def normal(self):
        return PointOnSurfaceNormal(self)


PointOnSurfacePosition = cast_expression("PointOnSurfacePosition", Vector, PointOnSurface)
PointOnSurfaceTangentU = unary_expression("PointOnSurfaceTangentU", Vector, PointOnSurface)
PointOnSurfaceTangentV = unary_expression("PointOnSurfaceTangentV", Vector, PointOnSurface)
PointOnSurfaceNormal = unary_expression("PointOnSurfaceNormal", Vector, PointOnSurface)

TransformSurface = binary_expression("TransformSurface", Surface, Transform, Surface)


class Circle(Curve):
    radius = Field(Scalar, default=1.0)
    normal = Field(Vector, default=Vector.Z)
    position = Field(Vector, default=Vector.ZERO)


class CubicBezier(Curve):
    p1 = Field(Vector)
    p2 = Field(Vector)
    p3 = Field(Vector)
    p4 = Field(Vector)


class CurveInstance(Expression):
    parent = Field(Object)
    curve = Field(Curve)

    @property
    def world_curve(self):
        return CurveInstanceWorld(self)


CurveInstanceWorld = unary_expression("CurveInstanceWorld", Curve, CurveInstance)
