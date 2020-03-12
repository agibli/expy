import sys

from six import with_metaclass

from . import type_conversions


class Field(object):

    _next_sort_order = 0

    def __init__(self, type=object, display_name=None, default=None):
        self.type = type
        self.display_name = display_name
        self.default = default
        self._sort_order = Field._next_sort_order
        Field._next_sort_order += 1

    def construct(self, value):
        return type_conversions.convert(self.type, value)


class FieldGetter(object):

    def __init__(self, index):
        self.index = index

    def __get__(self, obj, cls=None):
        if obj is not None:
            return obj._values[self.index]
        if cls is not None:
            return cls._fields[self.index]
        return self


class ExpressionMeta(type):

    def __new__(cls, name, bases, attrs):
        fields = []
        for base in bases:
            if isinstance(base, ExpressionMeta):
                fields.extend(base._fields)
        new_fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                v.name = k
                v.display_name = v.display_name or k
                new_fields.append(v)
        new_fields.sort(key=lambda f: f._sort_order)
        fields.extend(new_fields)
        for i, f in enumerate(fields):
            attrs[f.name] = FieldGetter(i)
        attrs["_fields"] = tuple(fields)
        attrs["__slots__"] = ("_values", "_hash")
        attrs.setdefault("__isabstractexpression__", False)
        attrs.setdefault("__new_expression__", None)
        return type.__new__(cls, name, bases, attrs)


def abstract_expression(cls):
    cls.__isabstractexpression__ = True
    if not getattr(cls, "__new_expression__", None):
        cls.__new_expression__ = type_conversions.constructor(cls)
    return cls


@abstract_expression
class Expression(with_metaclass(ExpressionMeta)):

    def __new__(cls, *args, **kwargs):
        if cls.__new_expression__:
            return cls.__new_expression__(*args, **kwargs)
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        if type(self).__isabstractexpression__:
            raise TypeError("Cannot initialize abstract type")
        try:
            self._values
        except AttributeError:
            if len(args) < len(self._fields):
                missing_fields = self._fields[len(args):]
                args += tuple(kwargs.pop(f.name, f.default) for f in missing_fields)
                if kwargs:
                    raise TypeError("Unexpected keyword argument")
            elif len(args) > len(self._fields):
                raise TypeError("Unexpected positional argument")
            args = tuple(f.construct(arg) for f, arg in zip(self._fields, args))
            self._values = args
            self._hash = None

    def __eq__(self, other):
        if id(self) == id(other):
            return True
        return type(self) == type(other) and self._values == other._values

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((type(self),) + self._values)
        return self._hash

    def __getnewargs__(self):
        return self._values

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__, ", ".join(repr(x) for x in self._values),
        )


expr = Expression


def _expression_type(name, base, attrs, module=None, depth=2):
    result = type(base)(name, (base,), attrs)
    if module is None:
        try:
            module = sys._getframe(depth).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    if module is not None:
        result.__module__ = module
    return result


def unary_expression(name, result_type, operand_type=None):
    if operand_type is None:
        operand_type = result_type
    class_namespace = {
        "operand": Field(operand_type),
    }
    return _expression_type(name, result_type, class_namespace)


def binary_expression(name, result_type, left_type=None, right_type=None):
    if left_type is None:
        left_type = result_type
    if right_type is None:
        right_type = left_type
    class_namespace = {
        "loperand": Field(left_type),
        "roperand": Field(right_type),
    }
    return _expression_type(name, result_type, class_namespace)


def cast_expression(name, result_type, from_type):
    class_namespace = {
        "value": Field(from_type),
    }
    result = _expression_type(name, result_type, class_namespace)
    type_conversions.register_conversion(result, from_type)
    type_conversions.register_conversion(from_type, result, lambda c: c.value)
    return result
