from __future__ import absolute_import

import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt

from ...expressions.math import *

from .context import (
    maya_builder,
    ValueResult,
    AttributeResult,
    CompoundResult,
)
from .expressions import (
    MayaBooleanAttribute,
    MayaIntegerAttribute,
    MayaScalarAttribute,
    MayaVectorAttribute,
    MayaMatrixAttribute,
)


@maya_builder.handler(MayaBooleanAttribute)
@maya_builder.handler(MayaIntegerAttribute)
@maya_builder.handler(MayaScalarAttribute)
@maya_builder.handler(MayaVectorAttribute)
@maya_builder.handler(MayaMatrixAttribute)
def _handle_attr_expression(context, expression):
    return AttributeResult(expression.value)


@maya_builder.handler(BooleanConstant)
@maya_builder.handler(IntegerConstant)
@maya_builder.handler(ScalarConstant)
def _handle_constant(context, expression):
    return ValueResult(expression.value)


@maya_builder.handler(VectorConstant)
def _handle_vector_constant(context, expression):
    return ValueResult(dt.Vector(*expression._values))


@maya_builder.handler(MatrixConstant)
def _handle_matrix_constant(context, expression):
    return ValueResult(dt.Matrix(*expression._values))


@maya_builder.handler(ScalarFromInteger)
@maya_builder.handler(ScalarFromBoolean)
@maya_builder.handler(IntegerFromBoolean)
def _handle_scalar_from_integer(context, expression):
    return context.get(expression.value)


@maya_builder.handler(IntegerFromScalar)
def _handle_integer_from_scalar(context, expression):
    clamp_node = pm.createNode("clamp")
    context.get(expression.value).assign(clamp_node.inputR)
    clamp_node.minR.set(-0.5)
    clamp_node.maxR.set(0.5)
    subtract_node = pm.createNode("plusMinusAverage")
    subtract_node.operation.set(2)
    context.get(expression.value).assign(subtract_node.input1D[0])
    clamp_node.outputR.connect(subtract_node.input1D[1])
    subtract_node.addAttr("roundedOutput1D", at="long")
    subtract_node.output1D.connect(subtract_node.roundedOutput1D)
    return AttributeResult(subtract_node.roundedOutput1D)


@maya_builder.handler(BooleanFromScalar)
@maya_builder.handler(BooleanFromInteger)
def _handle_boolean_from_scalar(context, expression):
    condition_node = pm.createNode("condition")
    context.get(expression.value).assign(condition_node.firstTerm)
    return AttributeResult(condition_node.outColorR)


@maya_builder.handler(BooleanInverse)
def _handle_boolean_inverse(context, expression):
    inv_node = pm.createNode("reverse")
    context.get(expression.operand).assign(inv_node.inputX)
    return AttributeResult(inv_node.outputX)


@maya_builder.handler(BooleanAnd)
def _handle_boolean_and(context, expression):
    and_node = pm.createNode("multiplyDivide")
    context.get(expression.loperand).assign(and_node.inputX)
    context.get(expression.roperand).assign(and_node.inputY)
    return AttributeResult(and_node.outputX)


@maya_builder.handler(BooleanOr)
def _handle_boolean_or(context, expression):
    or_node = pm.createNode("plusMinusAverage")
    context.get(expression.loperand).assign(or_node.input1D[0])
    context.get(expression.roperand).assign(or_node.input1D[1])
    or_node.addAttr("boolOutput1D", at="bool")
    or_node.output1D.connect(or_node.boolOutput1D)
    return AttributeResult(or_node.boolOutput1D)


def _handle_scalar_plus_minus_average(context, values, operation):
    util_node = pm.createNode("plusMinusAverage")
    util_node.operation.set(operation)
    for i, value in enumerate(values):
        context.get(value).assign(util_node.input1D[i])
    return AttributeResult(util_node.output1D)


def _expand_associative_binary_op(expression, left_associative=False):
    expression_type = type(expression)
    result = []
    left = expression.loperand
    right = expression.roperand
    if isinstance(left, expression_type):
        result.extend(_expand_associative_binary_op(
            left, left_associative=left_associative,
        ))
    else:
        result.append(left)
    if not left_associative and isinstance(right, expression_type):
        result.extend(_expand_associative_binary_op(
            right, left_associative=left_associative,
        ))
    else:
        result.append(right)
    return result


@maya_builder.handler(ScalarAdd)
def _handle_scalar_add(context, expression):
    values = _expand_associative_binary_op(expression)
    return _handle_scalar_plus_minus_average(context, values, 1)


@maya_builder.handler(ScalarSubtract)
def _handle_scalar_subtract(context, expression):
    values = _expand_associative_binary_op(expression, left_associative=True)
    return _handle_scalar_plus_minus_average(context, values, 2)


def _handle_scalar_multiply_divide_power(context, expression, operation):
    util_node = pm.createNode("multiplyDivide")
    util_node.operation.set(operation)
    context.get(expression.loperand).assign(util_node.input1X)
    context.get(expression.roperand).assign(util_node.input2X)
    return AttributeResult(util_node.outputX)


@maya_builder.handler(ScalarMultiply)
def _handle_scalar_multiply(context, expression):
    return _handle_scalar_multiply_divide_power(context, expression, 1)


@maya_builder.handler(ScalarDivide)
def _handle_scalar_divide(context, expression):
    return _handle_scalar_multiply_divide_power(context, expression, 2)


@maya_builder.handler(ScalarPower)
def _handle_scalar_divide(context, expression):
    return _handle_scalar_multiply_divide_power(context, expression, 3)


@maya_builder.handler(VectorFromScalar)
def _handle_vector_from_scalar(context, expression):
    x = context.get(expression.xvalue)
    y = context.get(expression.xvalue)
    z = context.get(expression.xvalue)
    return CompoundResult(x, y, z)


@maya_builder.handler(VectorComponent)
def _handle_vector_component(context, expression):
    vector_result = context.get(expression.value)
    return vector_result.child(expression.index)


def _handle_vector_plus_minus_average(context, values, operation):
    util_node = pm.createNode("plusMinusAverage")
    util_node.operation.set(operation)
    for i, value in enumerate(values):
        context.get(value).assign(util_node.input3D[i])
    return AttributeResult(util_node.output3D)


@maya_builder.handler(VectorAdd)
def _handle_vector_add(context, expression):
    values = _expand_associative_binary_op(expression)
    return _handle_vector_plus_minus_average(context, values, 1)


@maya_builder.handler(VectorSubtract)
def _handle_vector_subtract(context, expression):
    values = _expand_associative_binary_op(expression, left_associative=True)
    return _handle_vector_plus_minus_average(context, values, 2)


def _handle_vector_multiply_divide(context, expression, operation):
    util_node = pm.createNode("multiplyDivide")
    util_node.operation.set(operation)
    vector_result = context.get(expression.loperand)
    scalar_result = context.get(expression.roperand)
    vector_result.assign(util_node.input1)
    scalar_result.assign(util_node.input2X)
    scalar_result.assign(util_node.input2Y)
    scalar_result.assign(util_node.input2Z)
    return AttributeResult(util_node.output)


@maya_builder.handler(VectorMultiply)
def _handle_vector_multiply(context, expression):
    return _handle_vector_multiply_divide(context, expression, 1)


@maya_builder.handler(VectorDivide)
def _handle_vector_divide(context, expression):
    return _handle_vector_multiply_divide(context, expression, 2)


@maya_builder.handler(VectorDotProduct)
def _handle_dot_product(context, expression):
    dot_node = pm.createNode("vectorProduct")
    dot_node.operation.set(1)
    dot_node.normalizeOutput.set(False)
    context.get(expression.loperand).assign(dot_node.input1)
    context.get(expression.roperand).assign(dot_node.input2)
    return AttributeResult(dot_node.outputX)


@maya_builder.handler(VectorCrossProduct)
def _handle_cross_product(context, expression):
    cross_node = pm.createNode("vectorProduct")
    cross_node.operation.set(2)
    cross_node.normalizeOutput.set(False)
    context.get(expression.loperand).assign(cross_node.input1)
    context.get(expression.roperand).assign(cross_node.input2)
    return AttributeResult(cross_node.output)


@maya_builder.handler(VectorNormalize)
def _handle_normalize_vector(context, expression):
    return context.get(expression.operand / expression.operand.length())


@maya_builder.handler(VectorLength)
def _handle_vector_length(context, expression):
    dist_node = pm.createNode("distanceBetween")
    context.get(expression.operand).assign(dist_node.point1)
    return AttributeResult(dist_node.distance)


@maya_builder.handler(MatrixFromScalar)
def _handle_scalar_to_matrix(context, expression):
    matrix_node = pm.createNode("fourByFourMatrix")
    context.get(expression.a00).assign(matrix_node.in00)
    context.get(expression.a01).assign(matrix_node.in01)
    context.get(expression.a02).assign(matrix_node.in02)
    context.get(expression.a03).assign(matrix_node.in03)
    context.get(expression.a10).assign(matrix_node.in10)
    context.get(expression.a11).assign(matrix_node.in11)
    context.get(expression.a12).assign(matrix_node.in12)
    context.get(expression.a13).assign(matrix_node.in13)
    context.get(expression.a20).assign(matrix_node.in20)
    context.get(expression.a21).assign(matrix_node.in21)
    context.get(expression.a22).assign(matrix_node.in22)
    context.get(expression.a23).assign(matrix_node.in23)
    context.get(expression.a30).assign(matrix_node.in30)
    context.get(expression.a31).assign(matrix_node.in31)
    context.get(expression.a32).assign(matrix_node.in32)
    context.get(expression.a33).assign(matrix_node.in33)
    return AttributeResult(matrix_node.output)


@maya_builder.handler(MatrixInverse)
def _handle_matrix_inverse(context, expression):
    matrix = context.get(expression.operand)
    try:
        return matrix.inverse
    except AttributeError:
        pm.loadPlugin("matrixNodes", quiet=True)
        inverse_node = pm.createNode("inverseMatrix")
        matrix.assign(inverse_node.inputMatrix)
        return AttributeResult(inverse_nodeMatrix)


@maya_builder.handler(MatrixTranspose)
def _handle_matrix_transpose(context, expression):
    pm.loadPlugin("matrixNodes", quiet=True)
    transpose_node = pm.createNode("transposeMatrix")
    context.get(expression.operand).assign(inverse_node.inputMatrix)
    return AttributeResult(transpose_node.outputMatrix)


@maya_builder.handler(MatrixVectorMultiply)
def _handle_vector_matrix_multiply(context, expression):
    mult_node = pm.createNode("pointMatrixMult")
    context.get(expression.vector).assign(mult_node.inPoint)
    context.get(expression.matrix.transpose()).assign(mult_node.inMatrix)
    mult_node.vectorMultiply.set(True)
    return AttributeResult(mult_node.output)


@maya_builder.handler(VectorMatrixMultiply)
def _handle_vector_matrix_multiply(context, expression):
    mult_node = pm.createNode("pointMatrixMult")
    context.get(expression.vector).assign(mult_node.inPoint)
    context.get(expression.matrix).assign(mult_node.inMatrix)
    mult_node.vectorMultiply.set(True)
    return AttributeResult(mult_node.output)


@maya_builder.handler(MatrixMultiply)
def _handle_matrix_multiply(context, expression):
    mult_node = pm.createNode("multMatrix")
    context.get(expression.loperand).assign(mult_node.matrixIn[0])
    context.get(expression.roperand).assign(mult_node.matrixIn[1])
    return AttributeResult(mult_node.matrixSum)
