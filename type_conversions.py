from collections import OrderedDict, deque


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
        for func in self._find_conversion(to_type, type(from_value)):
            result = func(result)
        return result

    def constructor(self, to_type):
        def convert(from_value):
            return self.convert(to_type, from_value)
        return convert

    def is_convertible(self, to_type, from_type):
        try:
            self._find_conversion(to_type, from_type)
        except TypeError:
            return False
        else:
            return True

    def _find_conversion(self, to_type, from_type):
        if to_type == from_type:
            return ()
        try:
            path = self._path_cache[(to_type, from_type)]
        except KeyError:
            prev = {from_type: (None, None)}
            q = deque([from_type])
            tip = to_type
            while q:
                current = q.popleft()
                bases = current.mro()
                # If current type can be implicitly upcast to the destination,
                # we are done. Upcasting is not part of the conversion sequence,
                # just tweak the destination to the subclass we've arrived at.
                if to_type in bases:
                    tip = current
                    break
                # Explore conversions from any base class of the current type.
                # Conceptually, this introduces 0-length edges from the current
                # type to any of its bases.
                for base in bases:
                    conversions = self._conversions.get(base, {})
                    for neighbor, func in conversions.items():
                        if neighbor not in prev:
                            q.append(neighbor)
                            prev[neighbor] = (current, func)
            if tip in prev:
                reverse_path = []
                while tip is not None:
                    tip, func = prev[tip]
                    if func is not None:
                        reverse_path.append(func)
                path = tuple(reversed(reverse_path))
            else:
                # Destination type is unreachable
                path = None
            self._path_cache[(to_type, from_type)] = path
        if path is None:
            raise TypeError("Cannot convert type")
        return path


_instance = TypeConversions()
register_conversion = _instance.register_conversion
conversion = _instance.conversion
convert = _instance.convert
constructor = _instance.constructor
is_convertible = _instance.is_convertible
