from __future__ import division

import unittest

from expy import type_conversions
from expy.expressions.math import Matrix
from expy.expressions.transform import *
from expy.contexts.constant_folding import ConstantFoldingContext


def _var_type(name, base):
    return type(base)(name, (base,), {"tag": Field(str)})

TransformVar = _var_type("TransformVar", Transform)
MatrixVar = _var_type("MatrixVar", Matrix)
RotationVar = _var_type("RotationVar", Rotation)


class TestConstantFoldingTransform(unittest.TestCase):

    def _assert_const_almost_equal(self, const, value):
        self.assertIsInstance(const, type(value))
        for a, b in zip(const._values, value._values):
            self.assertAlmostEqual(a, b)

    def test_transform_identities(self):
        ctx = ConstantFoldingContext()
        self.assertEqual(
            ctx.get(
                ComposeTransform(
                    translation=Vector.ZERO,
                    rotation=EulerRotation(),
                    scale=Vector.ONES,
                )
            ),
            Transform.IDENTITY
        )

        T = TransformVar("T")
        P = TransformVar("P")
        M = MatrixVar("M")
        self.assertEqual(ctx.get(T.local_to_world(P).world_to_local(P)), T)
        self.assertEqual(ctx.get(T.world_to_local(P).local_to_world(P)), T)

        self.assertEqual(ctx.get(T.local_to_world(Transform.IDENTITY)), T)
        self.assertEqual(ctx.get(T.world_to_local(Transform.IDENTITY)), T)
        self.assertEqual(ctx.get(Transform.IDENTITY.local_to_world(T)), T)
        self.assertEqual(ctx.get(Transform.IDENTITY.world_to_local(T)), T)

        self.assertEqual(ctx.get(TransformFromMatrix(MatrixFromTransform(T))), T)
        self.assertEqual(ctx.get(MatrixFromTransform(TransformFromMatrix(M))), M)



    def test_transform_composition(self):
        ctx = ConstantFoldingContext()

        self._assert_const_almost_equal(
            ctx.get(
                ComposeTransform(
                    translation=VectorConstant(10, 20, 30),
                ).matrix
            ),
            MatrixConstant(
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                10.0, 20.0, 30.0, 1.0,
            )
        )

        self._assert_const_almost_equal(
            ctx.get(
                ComposeTransform(
                    rotation=EulerRotation(10, 20, 30),
                ).matrix
            ),
            MatrixConstant(
                0.813797681349, 0.469846310393, -0.342020143326, 0.0,
                -0.44096961053, 0.882564119259, 0.163175911167, 0.0,
                0.37852230637, 0.0180283112363, 0.925416578398, 0.0,
                0.0, 0.0, 0.0, 1.0,
            )
        )

        self._assert_const_almost_equal(
            ctx.get(
                ComposeTransform(
                    scale=VectorConstant(1, 2, 3)
                ).matrix
            ),
            MatrixConstant(
                1.0, 0.0, 0.0, 0.0,
                0.0, 2.0, 0.0, 0.0,
                0.0, 0.0, 3.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            )
        )

        self._assert_const_almost_equal(
            ctx.get(
                ComposeTransform(
                    translation=VectorConstant(10, 20, 30),
                    rotation=EulerRotation(10, 20, 30),
                    scale=VectorConstant(1, 2, 3),
                ).matrix,
            ),
            MatrixConstant(
                0.813797681349, 0.469846310393, -0.342020143326, 0.0,
                -0.88193922106, 1.76512823852, 0.326351822333, 0.0,
                1.13556691911, 0.0540849337089, 2.77624973519, 0.0,
                10.0, 20.0, 30.0, 1.0,
            )
        )

    def test_transform_decomposition(self):
        ctx = ConstantFoldingContext()
        M = MatrixConstant(
            0.813797681349, 0.469846310393, -0.342020143326, 0.0,
            -0.23090107598, 2.14100528683, 0.0527357076725, 0.0,
            -1.56251814218, -2.34746981397, -2.55693616031, 0.0,
            10.0, 20.0, 30.0, 1.0,
        )
        T = TransformFromMatrix(M)
        self._assert_const_almost_equal(
            ctx.get(T.translation), VectorConstant(10, 20, 30),
        )
        self._assert_const_almost_equal(
            ctx.get(T.scale), VectorConstant(1, 2, -3),
        )


if __name__ == '__main__':
    unittest.main()
