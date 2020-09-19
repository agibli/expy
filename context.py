from collections import namedtuple


class Context(object):

    def __init__(self, handler, parent=None):
        self.handler = handler
        self.parent = parent
        self._cache = {}

    def get(self, value):
        if self.parent:
            value = self.parent.get(value)
        try:
            result = self._cache[value]
        except KeyError:
            result = self._handle(value)
            self._cache[value] = result
        return result

    def _handle(self, value):
        return self.handler(self, value)


def _default_handler(context, value):
    raise NotImplementedError("Unsupported value: {}".format(value))


class ContextHandler(object):

    def __init__(self):
        self._handlers = {}
        self.default_handler = _default_handler

    def register_handler(self, value_type, handler):
        self._handlers[value_type] = handler

    def handler(self, value_type):
        def decorator(func):
            self.register_handler(value_type, func)
            return func
        return decorator

    def default(self):
        def decorator(func):
            self.default_handler = func
            return func
        return decorator

    def get_handler(self, value_type):
        if not isinstance(value_type, type):
            value_type = type(value_type)
        for base in value_type.mro():
            try:
                return self._handlers[base]
            except KeyError:
                continue
        return self.default_handler

    def __call__(self, context, value):
        return self.get_handler(value)(context, value)
