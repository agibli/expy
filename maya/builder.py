from ..builder import Builder


maya_builder = Builder()


class ValueResult(object):
    def __init__(self, value):
        self._value = value

    @property
    def is_varying(self):
        return False

    def assign(self, output):
        for conn in output.listConnections(s=True, d=False, p=True):
            conn.disconnect(output)
        output.set(self._value)

    def child(self, index):
        return ValueResult(self._value[index])

    def evaluate(self):
        return self._value


class AttributeResult(object):
    def __init__(self, attr, truncate=False):
        self._attr = attr

    @property
    def is_varying(self):
        return True

    def assign(self, output):
        self._attr.connect(output, f=True)

    def child(self, index):
        return AttributeResult(self._attr.children()[index])

    def evaluate(self):
        return self._attr.get()


class CompoundResult(object):
    def __init__(self, *children):
        self.children = children

    @property
    def size(self):
        return len(self.children)

    @property
    def is_varying(self):
        return any(c.is_varying for c in self.children)

    def assign(self, output):
        for a, b in zip(self.children, output.children()):
            a.assign(b)

    def child(self, index):
        return self.children[index]
