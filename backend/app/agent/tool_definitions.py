"""Shared types for pluggable task tools."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


ToolHandler = Callable[[str], dict[str, Any]]
ToolScorer = Callable[[str, str], "ToolScore"]


@dataclass(frozen=True)
class ToolScore:
    tool: str
    confidence: float
    signals: list[str]
    reason: str
    intent_detected: bool


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: ToolHandler
    score: ToolScorer


def build_tool_score(
    tool: str,
    confidence: float,
    signals: list[str],
    intent_detected: bool,
) -> ToolScore:
    return ToolScore(
        tool=tool,
        confidence=round(min(confidence, 0.99), 2),
        signals=signals,
        reason=", ".join(signals) if signals else "no matching signals",
        intent_detected=intent_detected,
    )
