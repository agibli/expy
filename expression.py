from six import with_metaclass

from . import type_conversions


class Field(object):

    _next_sort_order = 0

    def __init__(self, type=None, name=None, display_name=None, default=None):
        self.type = type
        self.name = name
        self.display_name = display_name
        self.default = default
        self._sort_order = Field._next_sort_order
        Field._next_sort_order += 1

    def construct(self, value):
        return self.type(value) if self.type else value


class ExpressionMeta(type):

    def __new__(cls, name, bases, attrs):
        fields = []
        for base in bases:
            if isinstance(base, ExpressionMeta):
                fields.extend(base._fields)
        unsorted_fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                v.name = v.name or k
                v.display_name = v.display_name or k
                unsorted_fields.append(v)
        fields.extend(sorted(unsorted_fields, key=lambda f: f._sort_order))
        attrs["_fields"] = fields
        attrs["__slots__"] = ("_values",)
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

    def __eq__(self, other):
        return type(self) == type(other) and self._values == other._values

    def __ne__(self, other):
        return type(self) != type(other) or self._values != other._values

    def __hash__(self):
        return hash((type(self),) + self._values)

    def __getnewargs__(self):
        return self._values

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__, ", ".join(repr(x) for x in self._values),
        )


expr = Expression


def unary_expression(name, result_type, operand_type=None):
    if operand_type is None:
        operand_type = result_type
    class_namespace = {
        "operand": Field(operand_type),
    }
    return type(result_type)(name, (result_type,), class_namespace)


def binary_expression(name, result_type, left_type=None, right_type=None):
    if left_type is None:
        left_type = result_type
    if right_type is None:
        right_type = left_type
    class_namespace = {
        "loperand": Field(left_type),
        "roperand": Field(right_type),
    }
    return type(result_type)(name, (result_type,), class_namespace)


def constant_expression(name, result_type, constant_type):
    subclass = unary_expression(name, result_type, constant_type)
    type_conversions.register_conversion(subclass, constant_type)
    return subclass
