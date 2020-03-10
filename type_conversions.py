from collections import OrderedDict


class TypeConversions(object):

    def __init__(self):
        self._conversions = OrderedDict()
        self._path_cache = {}

    def register_conversion(self, to_type, from_type, func=None):
        if func is None:
            func = to_type
        self._conversions.setdefault(from_type, OrderedDict())[to_type] = func
        self._path_cache = {}

    def conversion(self, to_type, from_type):
        def conversion_decorator(func):
            self.register_conversion(to_type, from_type, func)
            return func
        return conversion_decorator

    def convert(self, to_type, from_value):
        result = from_value
        for func in self._conversion_path(to_type, type(from_value)):
            result = func(result)
        return result

    def constructor(self, to_type):
        def convert(from_value):
            return self.convert(to_type, from_value)
        return convert

    def is_convertible(self, to_type, from_type):
        try:
            self._conversion_path(to_type, from_type)
        except TypeError:
            return False
        else:
            return True

    def _conversion_path(self, to_type, from_type):
        if to_type == from_type:
            return ()
        try:
            path = self._path_cache[(to_type, from_type)]
        except KeyError:
            path = None
            self._path_cache[(to_type, from_type)] = None
            for base in from_type.mro():
                if path is not None:
                    break
                if to_type == base:
                    path = ()
                else:
                    conversions = self._conversions.get(base, {})
                    for mid_type, func in conversions.items():
                        try:
                            rest = self._conversion_path(to_type, mid_type)
                            if path is None or len(rest) < len(path) - 1:
                                path = (func,) + rest
                        except TypeError:
                            pass
            self._path_cache[(to_type, from_type)] = path
        if path is None:
            raise TypeError("Unable to convert type")
        return path


_instance = TypeConversions()
register_conversion = _instance.register_conversion
conversion = _instance.conversion
convert = _instance.convert
constructor = _instance.constructor
is_convertible = _instance.is_convertible
