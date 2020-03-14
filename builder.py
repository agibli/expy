from collections import namedtuple

from .expression import Expression


class BuilderBase(object):

    class Context(object):
        def __init__(self, builder):
            self.builder = builder
            self._cache = {}

        def get(self, expression):
            try:
                result = self._cache[expression]
            except KeyError:
                result = self.builder._build(self, expression)
                self.put(expression, result)
            return result

        def put(self, expression, result):
            self._cache[expression] = result

    def context(self):
        return self.Context(self)

    def _build(self, context, expression):
        raise NotImplementedError("Unsupported expression")


class Builder(BuilderBase):

    _HandlerInfo = namedtuple("_HandlerInfo", ["func", "propagate"])

    def __init__(self):
        super(Builder, self).__init__()
        self._handlers = {}
        self._default_handler = None

    def register_handler(self, expression_type, handler, propagate=True):
        self._handlers[expression_type] = self._HandlerInfo(handler, propagate)

    def handler(self, expression_type, propagate=True):
        def decorator(func):
            self.register_handler(expression_type, func, propagate)
            return func
        return decorator

    def set_default_handler(self, handler, propagate=True):
        self._default_handler = self._HandlerInfo(handler, propagate)

    def default_handler(self, propagate=True):
        def decorator(func):
            self.set_default_handler(func, propagate)
            return func
        return decorator

    def _get_handler(self, expression_type):
        if not isinstance(expression_type, type):
            expression_type = type(expression_type)
        for base in expression_type.mro():
            try:
                return self._handlers[base]
            except KeyError:
                continue
        if self._default_handler is None:
            raise NotImplementedError(
                "Unsupported expression: {}".format(expression_type.__name__)
            )
        return self._default_handler

    def _build(self, context, expression):
        seen = set()
        stack = [expression]
        pending = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            handler = self._get_handler(x)
            pending.append((x, handler))
            if handler.propagate:
                for value in x._values:
                    if isinstance(value, Expression):
                        stack.append(value)
        while pending:
            x, handler = pending.pop()
            result = handler.func(context, x)
            context.put(x, result)
        return result


class Pipeline(BuilderBase):

    class Context(BuilderBase.Context):
        def __init__(self, builder):
            super(Pipeline.Context, self).__init__(builder)
            self.children = tuple(s.context() for s in builder.stages)

    def __init__(self, stages):
        super(Pipeline, self).__init__()
        self.stages = list(stages)

    def _build(self, context, expression):
        result = expression
        for child_context in context.children:
            result = child_context.get(result)
        return result
