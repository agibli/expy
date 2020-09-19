from ...expression import Expression
from ...context import Context, ContextHandler


constant_folding = ContextHandler()


@constant_folding.handler(Expression)
def _constant_folding_default_handler(context, expression):
    fold = lambda f: context.get(f) if isinstance(f, Expression) else f
    return type(expression)(*(map(fold, expression._values)))


class ConstantFoldingContext(Context):
    def __init__(self):
        super(ConstantFoldingContext, self).__init__(handler=constant_folding)
