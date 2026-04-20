"""Calculator tool for simple arithmetic app"""

import ast
import operator
import re
from typing import Union

from app.agent.tool_definitions import ToolDefinition, ToolScore, build_tool_score


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def calculate(task: str) -> dict:
    expression = _extract_expression(task)
    try:
        result = _evaluate(expression)
    except ZeroDivisionError as exc:
        raise ValueError("Division by zero is not supported.") from exc

    return {
        "final_output": str(result),
        "metadata": {
            "expression": expression,
        },
    }


def _extract_expression(task: str) -> str:
    match = re.search(r"(-?\d+(?:\.\d+)?(?:\s*[\+\-\*\/]\s*-?\d+(?:\.\d+)?)+)", task)
    if not match:
        raise ValueError("No supported arithmetic expression found.")
    return match.group(1).strip()


def _evaluate(expression: str) -> Union[float, int]:
    node = ast.parse(expression, mode="eval")
    value = _eval_node(node.body)
    return int(value) if isinstance(value, float) and value.is_integer() else value


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        operand = _eval_node(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](operand)
    raise ValueError("Unsupported arithmetic expression.")


def score_calculator_tool(task: str, clean_task: str) -> ToolScore:
    confidence = 0.0
    matches: list[str] = []
    intent_detected = False

    expression_match = re.search(r"-?\d+(?:\.\d+)?\s*[\+\-\*\/]\s*-?\d+(?:\.\d+)?", task)
    if expression_match:
        confidence += 0.8
        matches.append("matched arithmetic expression")
        intent_detected = True

    math_keywords = ["calculate", "math", "sum", "multiply", "divide", "subtract", "add"]
    if any(keyword in clean_task for keyword in math_keywords):
        confidence += 0.2
        matches.append("matched math keyword")
        intent_detected = True

    return build_tool_score("calculator", confidence, matches, intent_detected)


CALCULATOR_TOOL = ToolDefinition(
    name="calculator",
    handler=calculate,
    score=score_calculator_tool,
)
