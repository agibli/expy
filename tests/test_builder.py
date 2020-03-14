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

    def test_propagate(self):
        class Int(Expression):
            k = Field(int)

        class Add(Expression):
            l = Field(Expression)
            r = Field(Expression)

        class LazyAdd(Expression):
            l = Field(Expression)
            r = Field(Expression)

        builder = Builder()
        eval_order = []
    
        @builder.handler(Int)
        def handle_int(ctx, expr):
            eval_order.append(expr)
            return expr.k
        
        @builder.handler(Add, propagate=True)
        def handle_add(ctx, expr):
            eval_order.append(expr)
            return ctx.get(expr.l) + ctx.get(expr.r)

        @builder.handler(LazyAdd, propagate=False)
        def handle_lazy_add(ctx, expr):
            eval_order.append(expr)
            return ctx.get(expr.l) + ctx.get(expr.r)

        ctx = builder.context()
        c1 = Int(1)
        c2 = Int(2)
        c3 = Int(3)
        a2 = LazyAdd(c2, c3)
        a1 = Add(c1, a2)
        self.assertEqual(ctx.get(a1), 6)
        self.assertListEqual(eval_order, [c1, a2, c2, c3, a1])

    def test_pipeline(self):
        class In(Expression): pass
        class Tmp1(Expression): pass
        class Tmp2(Expression): pass
        class Out(Expression): pass

        stage1 = Builder()
        stage2part1 = Builder()
        stage2part2 = Builder()
        stage2 = Pipeline([stage2part1, stage2part2])
        builder = Pipeline([stage1, stage2])

        stage1.register_handler(In, lambda ctx,expr: Tmp1())
        stage2part1.register_handler(Tmp1, lambda ctx,expr: Tmp2())
        stage2part2.register_handler(Tmp2, lambda ctx,expr: Out())

        ctx = builder.context()
        self.assertEqual(ctx.get(In()), Out())
