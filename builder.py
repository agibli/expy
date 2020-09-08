from collections import namedtuple

from .expression import Expression


class BuildContextBase(object):
    def __init__(self):
        self._cache = {}

    def get(self, expression):
        try:
            result = self._cache[expression]
        except KeyError:
            result = self._build(expression)
            self._cache[expression] = result
        return result

    def _build(self, expression):
        raise NotImplementedError("Unsupported expression: {}".format(expression))


class BuildContext(BuildContextBase):
    def __init__(self, builder):
        super(BuildContext, self).__init__()
        self.builder = builder

    def _build(self, expression):
        return self.builder.call_handler(self, expression)


class Builder(object):

    def __init__(self):
        super(Builder, self).__init__()
        self._handlers = {}

    def register_handler(self, expression_type, handler):
        self._handlers[expression_type] = handler

    def handler(self, expression_type):
        def decorator(func):
            self.register_handler(expression_type, func)
            return func
        return decorator

    def get_handler(self, expression_type):
        if not isinstance(expression_type, type):
            expression_type = type(expression_type)
        for base in expression_type.mro():
            try:
                return self._handlers[base]
            except KeyError:
                continue
        return self.default_handler

    def default_handler(self, context, expression):
        raise NotImplementedError("Unsupported expression: {}".format(expression))

    def call_handler(self, context, expression):
        return self.get_handler(expression)(context, expression)

    def context(self):
        return BuildContext(self)


class PipelineContext(BuildContextBase):
    def __init__(self, stages):
        super(PipelineContext, self).__init__()
        self.stages = stages

    def _build(self, expression):
        result = expression
        for stage in self.stages:
            result = stage.get(result)
        return result
