"""Simple text operations word count, upper/lowercase app"""

import re

from app.agent.tool_definitions import ToolDefinition, ToolScore, build_tool_score


def process_text(task: str) -> dict:
    normalized = task.lower()
    operation = "word_count"

    if "uppercase" in normalized or "upper case" in normalized:
        operation = "uppercase"
    elif "lowercase" in normalized or "lower case" in normalized:
        operation = "lowercase"
    elif "word count" in normalized or "count words" in normalized:
        operation = "word_count"

    text = _extract_text(task, operation)

    if operation == "uppercase":
        output = text.upper()
    elif operation == "lowercase":
        output = text.lower()
    else:
        words = re.findall(r"\b\w+\b", text)
        output = f"Word count: {len(words)}"

    return {
        "final_output": output,
        "metadata": {
            "operation": operation,
            "input_text": text,
        },
    }


def _extract_text(task: str, operation: str) -> str:
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', task)
    if quoted:
        first = quoted[0]
        return next(part for part in first if part)

    patterns = {
        "uppercase": r"(?i)(?:uppercase|upper case|convert to uppercase)\s*(.+)",
        "lowercase": r"(?i)(?:lowercase|lower case|convert to lowercase)\s*(.+)",
        "word_count": r"(?i)(?:word count|count words(?: in)?)\s*(.+)",
    }
    match = re.search(patterns[operation], task)
    if match and match.group(1).strip():
        return match.group(1).strip(" :.-")

    return task.strip()


def score_text_tool(task: str, clean_task: str) -> ToolScore:
    confidence = 0.1
    matches = ["safe default for general text tasks"]
    intent_detected = False

    case_keywords = ["uppercase", "upper case", "lowercase", "lower case"]
    if any(keyword in clean_task for keyword in case_keywords):
        confidence += 0.7
        matches.append("matched case transformation keyword")
        intent_detected = True

    count_keywords = ["word count", "count words"]
    if any(keyword in clean_task for keyword in count_keywords):
        confidence += 0.7
        matches.append("matched word count keyword")
        intent_detected = True

    return build_tool_score("text_processor", confidence, matches, intent_detected)


TEXT_PROCESSOR_TOOL = ToolDefinition(
    name="text_processor",
    handler=process_text,
    score=score_text_tool,
)
