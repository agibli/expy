import sys
import itertools

from six import with_metaclass

from . import type_conversions


class Field(object):

    _sort_order_count = itertools.count()

    def __init__(self, type=object, display_name=None, default=None):
        self.type = type
        self.name = None
        self.display_name = display_name
        self.default = default
        self._sort_order = next(Field._sort_order_count)

    def construct(self, value):
        return type_conversions.convert(self.type, value)

    def index(self, expression_type):
        if not isinstance(expression_type, type):
            expression_type = type(expression_type)
        try:
            return expression_type._field_indices[self]
        except KeyError:
            raise ValueError("Not a field of type {}".format(expression_type))

    def get(self, expression):
        return expression._values[self.index(expression)]


class FieldGetter(object):

    def __init__(self, index):
        self.index = index

    def __get__(self, obj, cls=None):
        if obj is not None:
            return obj._values[self.index]
        if cls is not None:
            return cls._fields[self.index]
        return self


class SelfType(object): pass


class Output(object):

    _sort_order_count = itertools.count()

    def __init__(self, type):
        self.type = type
        self.name = None
        self._self_type = None
        self._expression_type = None
        self._sort_order = next(Field._sort_order_count)

    @property
    def expression_type(self):
        if self._expression_type is None:
            def __repr__(self_):
                return "{!r}.{}".format(self_.self, self.name)
            output_class_name = "{}.{}".format(self._self_type.__name__, self.name)
            output_class_attrs = {
                "self": Field(self._self_type),
                "__repr__": __repr__,
            }
            self._expression_type = _expression_type(
                output_class_name, self.type, output_class_attrs,
            )
        return self._expression_type

    def index(self, expression_type):
        if not isinstance(expression_type, type):
            expression_type = type(expression_type)
        try:
            return expression_type._output_indices[self]
        except KeyError:
            raise ValueError("Not an output of type {}".format(expression_type))

    def get(self, expression):
        return self.expression_type(expression)

    def __get__(self, obj, cls=None):
        if obj is not None:
            return self.expression_type(obj)
        if cls is not None:
            return self.expression_type
        return self


class ExpressionMeta(type):

    def __new__(cls, name, bases, attrs):
        fields = []
        outputs = []
        for base in bases:
            if isinstance(base, ExpressionMeta):
                fields.extend(base._fields)
                outputs.extend(base._outputs)

        new_fields = []
        new_outputs = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                v.name = k
                v.display_name = v.display_name or v.name
                new_fields.append(v)
            if isinstance(v, Output):
                v.name = k
                new_outputs.append(v)

        new_fields.sort(key=lambda f: f._sort_order)
        new_outputs.sort(key=lambda f: f._sort_order)

        fields.extend(new_fields)
        outputs.extend(new_outputs)

        for i, f in enumerate(fields):
            attrs[f.name] = FieldGetter(i)

        attrs["_fields"] = tuple(fields)
        attrs["_field_indices"] = { f: i for i, f in enumerate(fields) }

        attrs["_outputs"] = tuple(outputs)
        attrs["_output_indices"] = { o: i for i, o in enumerate(outputs) }

        attrs["__slots__"] = ("_values", "_hash")
        attrs.setdefault("__isabstractexpression__", False)

        result = type.__new__(cls, name, bases, attrs)
        for output in new_outputs:
            output._self_type = result
            if output.type is SelfType:
                output.type = result
        return result


def abstract_expression(cls):
    cls.__isabstractexpression__ = True
    return cls


@abstract_expression
class Expression(with_metaclass(ExpressionMeta)):

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


def expr(arg, type=Expression):
    return type_conversions.convert(type, arg)


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
