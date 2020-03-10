from six import with_metaclass

from . import type_conversions


class Field(object):

    _next_sort_order = 0

    def __init__(self, type=None, display_name=None, default=None):
        self.type = type
        self.display_name = display_name
        self.default = default
        self._sort_order = Field._next_sort_order
        Field._next_sort_order += 1

    def construct(self, value):
        return self.type(value) if self.type else value


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
