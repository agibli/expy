from ...expression import Expression
from ...builder import Builder


constant_folding = Builder()


@constant_folding.handler(Expression)
def _constant_folding_default_handler(context, expression):
    fold = lambda f: context.get(f) if isinstance(f, Expression) else f
    return type(expression)(*(map(fold, expression._values)))
