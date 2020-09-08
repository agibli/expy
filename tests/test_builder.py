import unittest

from expy.expression import Expression, Field
from expy.builder import *


class TestBuilder(unittest.TestCase):

    def test_unhandled(self):
        class A(Expression): pass
        class B(Expression): pass
        builder = Builder()
        builder.register_handler(A, lambda ctx,a: a)
        ctx = builder.context()
        ctx.get(A())
        self.assertRaises(NotImplementedError, lambda: ctx.get(B()))

    def test_base_handler(self):
        class Base(Expression): pass
        class Sub(Base): pass
        class Result(): pass
        result = Result()
        builder = Builder()
        builder.register_handler(Base, lambda ctx,a: result)
        self.assertEqual(builder.context().get(Sub()), result)

    def test_context_cache(self):
        class A(Expression): pass
        count = [0]
        builder = Builder()
        @builder.handler(A)
        def handle_a(ctx, expr):
            count[0] += 1
            return expr
        ctx = builder.context()
        ctx.get(A())
        ctx.get(A())
        self.assertEqual(count[0], 1)

    def test_pipeline(self):
        class In(Expression): pass
        class Tmp1(Expression): pass
        class Tmp2(Expression): pass
        class Out(Expression): pass

        stage1 = Builder()
        stage2part1 = Builder()
        stage2part2 = Builder()

        stage1.register_handler(In, lambda ctx,expr: Tmp1())
        stage2part1.register_handler(Tmp1, lambda ctx,expr: Tmp2())
        stage2part2.register_handler(Tmp2, lambda ctx,expr: Out())

        ctx = PipelineContext([
            stage1.context(),
            PipelineContext([
                stage2part1.context(),
                stage2part2.context()
            ])
        ])
        self.assertEqual(ctx.get(In()), Out())


if __name__ == '__main__':
    unittest.main()
