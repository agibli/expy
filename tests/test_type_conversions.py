import unittest

from expy.type_conversions import TypeConversions


def test_class(name):
    def __init__(self, arg=None):
        self.arg = arg
    def __eq__(self, other):
        return (type(self), self.arg) == (type(other), other.arg)
    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.arg or "")
    attrs = {"__init__": __init__, "__eq__": __eq__, "__repr__": __repr__}
    return type(name, (), attrs)


def gen_test_classes(count):
    for i in range(count):
        yield test_class(chr(ord('A') + i))


class TestTypeConversions(unittest.TestCase):

    def test_intermediate(self):
        A, B, C = gen_test_classes(3)
        conv = TypeConversions()
        conv.register_conversion(A, B)
        conv.register_conversion(B, C)
        self.assertEqual(conv.convert(A, B()), A(B()))
        self.assertEqual(conv.convert(B, C()), B(C()))
        self.assertEqual(conv.convert(A, C()), A(B(C())))

    def test_simplex(self):
        A, B, C = gen_test_classes(3)
        conv = TypeConversions()
        conv.register_conversion(A, B)
        conv.register_conversion(B, C)
        conv.register_conversion(C, A)
        self.assertEqual(conv.convert(A, B()), A(B()))
        self.assertEqual(conv.convert(A, C()), A(B(C())))
        self.assertEqual(conv.convert(B, A()), B(C(A())))
        self.assertEqual(conv.convert(B, C()), B(C()))
        self.assertEqual(conv.convert(C, A()), C(A()))
        self.assertEqual(conv.convert(C, B()), C(A(B())))

    def test_implicit_upcast_to(self):
        A, B = gen_test_classes(2)
        class ASub(A): pass
        conv = TypeConversions()
        conv.register_conversion(ASub, B)
        self.assertEqual(conv.convert(A, ASub()), ASub())
        self.assertEqual(conv.convert(A, B()), ASub(B()))

    def test_implicit_upcast_from(self):
        A, B = gen_test_classes(2)
        class BSub(B): pass
        conv = TypeConversions()
        conv.register_conversion(A, B)
        self.assertEqual(conv.convert(A, BSub()), A(BSub()))

    def test_breadth_search(self):
        A, B, C, D = gen_test_classes(4)
        conv = TypeConversions()
        conv.register_conversion(A, B)
        conv.register_conversion(A, C)
        conv.register_conversion(C, D)
        self.assertEqual(conv.convert(A, D()), A(C(D())))

    def test_shortest_path(self):
        A, B, C, D, E = gen_test_classes(5)
        conv = TypeConversions()
        conv.register_conversion(A, B)
        conv.register_conversion(B, C)
        conv.register_conversion(C, E)
        conv.register_conversion(A, D)
        conv.register_conversion(D, E)
        self.assertEqual(conv.convert(A, E()), A(D(E())))
