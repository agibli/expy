from __future__ import absolute_import

from ...expressions.scene import *
from ...expressions.transform import *
from .context import constant_folding


@constant_folding.handler(Object.parent)
def _handle_parent(context, expression):
    obj = context.get(expression.self)
    if isinstance(obj, RootObject):
        return Object.ROOT
    return obj.parent


@constant_folding.handler(Object.world)
def _handle_world(context, expression):
    obj = context.get(expression.self)
    if isinstance(obj, RootObject):
        return Transform.IDENTITY
    if isinstance(obj.parent, RootObject):
        return obj.local
    return obj.world


@constant_folding.handler(Object.local)
def _handle_local(context, expression):
    obj = context.get(expression.self)
    if isinstance(obj, RootObject):
        return Transform.IDENTITY
    return obj.local
