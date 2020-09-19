from __future__ import absolute_import

try:
    import pymel.core
    include_maya_tests = True
except ImportError:
    include_maya_tests = False

from .test_expression import *
from .test_builder import *
from .test_math_expressions import *
from .test_constant_folding import *

if include_maya_tests:
    from .maya import *
