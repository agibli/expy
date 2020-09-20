import pymel.core as pm
import pymel.core.datatypes as dt

from ...contexts.constant_folding import ConstantFoldingContext
from ...context import Context, ContextHandler


maya_builder = ContextHandler()


class MayaBuildContext(Context):
    def __init__(self):
        super(MayaBuildContext, self).__init__(
            handler=maya_builder,
            parent=ConstantFoldingContext(),
        )


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


class LocalMatrixAttributeResult(AttributeResult):
    def __init__(self, transform, inverse=False):
        attr = transform.inverseMatrix if inverse else transform.matrix
        super(LocalMatrixAttributeResult, self).__init__(attr)
        self.transform = transform
        self.is_inverse = inverse

    @property
    def inverse(self):
        return LocalMatrixAttributeResult(
            self.transform, inverse=not self.is_inverse,
        )

    @property
    def decompose(self):
        return ObjectLocalTransformResult(self.transform)


class WorldMatrixAttributeResult(AttributeResult):
    def __init__(self, transform, inverse=False):
        attr = transform.worldInverseMatrix[0] if inverse else transform.worldMatrix[0]
        super(WorldMatrixAttributeResult, self).__init__(attr)
        self.transform = transform
        self.is_inverse = inverse

    @property
    def inverse(self):
        return WorldMatrixAttributeResult(
            self.transform, inverse=not self.is_inverse,
        )

    @property
    def decompose(self):
        return ObjectWorldTransformResult(self.transform)


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


class TransformResult(object):
    def __init__(self, translation, rotation, scale):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def assign_transform(self, transform):
        self.translation.assign(transform.translate)
        self.rotation.assign_transform(transform)
        self.scale.assign(transform.scale)

    def is_world_transform_of(self, transform):
        return False

    def to_local(self, other):
        raise NotImplementedError()

    def to_world(self, other):
        raise NotImplementedError()


class ObjectLocalTransformResult(TransformResult):
    def __init__(self, transform):
        super(ObjectLocalTransformResult, self).__init__(
            translation=AttributeResult(transform.translate),
            rotation=EulerRotationResult(
                angles=AttributeResult(transform.rotate),
                order=AttributeResult(transform.rotateOrder),
            ),
            scale=AttributeResult(transform.scale),
        )
        self.transform = transform

    @property
    def matrix(self):
        return LocalMatrixAttributeResult(self.transform)

    def is_world_transform_of(self, transform):
        return (
            not self.transform.getParent()
            and self.transform == transform
        )

    def to_world(self, other):
        if other.is_world_transform_of(self.transform.getParent()):
            return ObjectWorldTransformResult(self.transform)
        raise NotImplementedError


class MatrixTransformResult(object):
    def __init__(self, matrix, rotate_order=ValueResult(0)):
        self.matrix = matrix
        self.rotate_order = rotate_order
        self._decompose_result = None

    @property
    def translation(self):
        return self._decompose().translation

    @property
    def rotation(self):
        return self._decompose().rotation

    @property
    def scale(self):
        return self._decompose().scale

    def assign_transform(self, transform):
        self._decompose().assign_transform(transform)

    def to_local(self, other):
        raise NotImplementedError()

    def to_world(self, other):
        raise NotImplementedError()

    def _decompose(self):
        if self._decompose_result is None:
            pm.loadPlugin("matrixNodes", quiet=True)
            decompose = pm.createNode("decomposeMatrix")
            self.matrix.assign(decompose.inputMatrix)
            self.rotate_order.assign(decompose.inputRotateOrder)
            self._decompose_result = TransformResult(
                translation=AttributeResult(decompose.outputTranslate),
                rotation=EulerRotationResult(
                    angles=AttributeResult(decompose.outputRotate),
                    order=AttributeResult(decompose.inputRotateOrder),
                ),
                scale=AttributeResult(decompose.outputScale),
            )
        return self._decompose_result


class ObjectWorldTransformResult(MatrixTransformResult):
    def __init__(self, transform, rotate_order=None):
        rotate_order = rotate_order or AttributeResult(transform.rotateOrder)
        matrix = WorldMatrixAttributeResult(transform)
        super(ObjectWorldTransformResult, self).__init__(matrix, rotate_order)
        self.transform = transform

    def is_world_transform_of(self, transform):
        return self.transform == transform

    def to_local(self, other):
        if other.is_world_transform_of(self.transform.getParent()):
            return ObjectLocalTransformResult(self.transform)
        raise NotImplementedError


class EulerRotationResult(object):
    def __init__(self, angles=ValueResult(dt.Vector()), order=ValueResult(0)):
        self.angles = angles
        self.order = order

    def assign_transform(self, transform):
        self.assign_euler_and_order(transform.rotate, transform.rotateOrder)

    def assign_euler_and_order(self, rotate_attr, order_attr):
        self.angles.assign(rotate_attr)
        self.order.assign(order_attr)

    def assign_euler(self, attr, order=0):
        self.angles.assign(transform.attr)

    def assign_compose_matrix(self, compose):
        self.assign_euler_and_order(compose.inputRotate, compose.inputRotateOrder)
        compose.useEulerRotation.set(True)
