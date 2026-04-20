
import re
from dataclasses import dataclass
from typing import Any, Optional

from app.agent.audit_logger import AuditLogger
from app.agent.tool_definitions import ToolDefinition, ToolScore
from app.tools.calculator import CALCULATOR_TOOL
from app.tools.text_processor import TEXT_PROCESSOR_TOOL
from app.tools.weather_mock import WEATHER_TOOL


class TaskRejectedError(ValueError):
    def __init__(
        self,
        message: str,
        execution_steps: list[dict[str, Any]],
        selected_tool: str = "rejected",
        tools_used: Optional[list[str]] = None,
    ) -> None:
        super().__init__(message)
        self.execution_steps = execution_steps
        self.selected_tool = selected_tool
        self.tools_used = tools_used or []


@dataclass
class IntentAnalysis:
    candidates: list[ToolScore]
    matched_intents: list[str]
    compound_detected: bool
    top_candidate: ToolScore


@dataclass
class RouteDecision:
    selected_tool: str
    confidence: float
    selection_reason: str
    fallback_used: bool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {
            TEXT_PROCESSOR_TOOL.name: TEXT_PROCESSOR_TOOL,
            CALCULATOR_TOOL.name: CALCULATOR_TOOL,
            WEATHER_TOOL.name: WEATHER_TOOL,
        }

    def get(self, name: str) -> ToolDefinition:
        return self._tools[name]

    def all(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def names(self) -> list[str]:
        return list(self._tools.keys())


class TaskController:
    CONFIDENCE_THRESHOLD = 0.40
    MULTI_INTENT_THRESHOLD = 2

    def __init__(self, registry: Optional[ToolRegistry] = None) -> None:
        self.registry = registry or ToolRegistry()

    def run_task(self, task: str) -> dict:
        audit_logger = AuditLogger()
        audit_logger.record_step("received", "Task received by controller", task=task)
        tool_name = "rejected"

        try:
            clean_task = self._validate_inputs(task, audit_logger)
            intent_analysis = self._analyze_intent(task, clean_task, audit_logger)
            route_decision = self._resolve_route(intent_analysis, audit_logger)
            tool_name = route_decision.selected_tool
            tool_definition = self.registry.get(tool_name)

            audit_logger.record_step(
                "execute",
                "Executing selected tool",
                selected_tool=tool_name,
                confidence=route_decision.confidence,
                selection_reason=route_decision.selection_reason,
                fallback_used=route_decision.fallback_used,
            )
            result = tool_definition.handler(task)
            audit_logger.record_step(
                "complete",
                "Tool execution completed",
                output=result["final_output"],
                metadata=result["metadata"],
                confidence=route_decision.confidence,
                selection_reason=route_decision.selection_reason,
            )

            return {
                "task": task,
                "final_output": result["final_output"],
                "selected_tool": tool_name,
                "tools_used": [tool_name],
                "execution_steps": audit_logger.export_steps(),
            }
        except ValueError as exc:
            audit_logger.record_step(
                "failed",
                "Task execution rejected",
                error=str(exc),
                error_type=type(exc).__name__,
                selected_tool=tool_name,
            )
            raise TaskRejectedError(
                str(exc),
                execution_steps=[step.model_dump() for step in audit_logger.export_steps()],
                selected_tool=tool_name,
                tools_used=[tool_name] if tool_name != "rejected" else [],
            ) from exc

    def _validate_inputs(self, task: str, audit_logger: AuditLogger) -> str:
        clean_text = task.strip()
        if not clean_text:
            raise ValueError("Task cannot be empty.")

        if len(clean_text) > 500:
            raise ValueError("Task must be 500 characters or fewer.")

        if not re.search(r"[A-Za-z0-9]", clean_text):
            raise ValueError("Task must include letters or numbers.")

        audit_logger.record_step(
            "validate",
            "Pre-execution validation passed",
            task_length=len(clean_text),
            has_alphanumeric=True,
        )
        return clean_text.lower()

    def _analyze_intent(self, task: str, clean_task: str, audit_logger: AuditLogger) -> IntentAnalysis:
        tool_scores = [tool.score(task, clean_task) for tool in self.registry.all()]
        sorted_scores = sorted(tool_scores, key=lambda tool_score: tool_score.confidence, reverse=True)
        matched_intents = [score.tool for score in sorted_scores if score.intent_detected]
        compound_detected = self._multi_intents(tool_scores)
        audit_logger.record_step(
            "analyze_intent",
            "Analyzed task intent candidates",
            candidates=[self._tool_dict(tool_score) for tool_score in sorted_scores],
            matched_intents=matched_intents,
            compound_detected=compound_detected,
            confidence_threshold=self.CONFIDENCE_THRESHOLD,
        )

        return IntentAnalysis(
            candidates=sorted_scores,
            matched_intents=matched_intents,
            compound_detected=compound_detected,
            top_candidate=sorted_scores[0],
        )

    def _resolve_route(self, analysis: IntentAnalysis, audit_logger: AuditLogger) -> RouteDecision:
        if analysis.compound_detected:
            audit_logger.record_step(
                "route",
                "Rejected multi intent task during routing",
                matched_intents=analysis.matched_intents,
                top_candidate=analysis.top_candidate.tool,
                top_confidence=analysis.top_candidate.confidence,
                determination="Enter one intent at a time.",
            )
            raise ValueError(
                "This request includes multiple intents. Please enter one intent at a time."
            )

        if analysis.top_candidate.confidence >= self.CONFIDENCE_THRESHOLD:
            audit_logger.record_step(
                "route",
                "Resolved task to a single tool",
                selected_tool=analysis.top_candidate.tool,
                confidence=analysis.top_candidate.confidence,
                reason=analysis.top_candidate.reason,
            )
            return RouteDecision(
                selected_tool=analysis.top_candidate.tool,
                confidence=analysis.top_candidate.confidence,
                selection_reason=analysis.top_candidate.reason,
                fallback_used=False,
            )

        audit_logger.record_step(
            "route",
            "Intent could not be resolved to a supported single-tool task",
            top_candidate=analysis.top_candidate.tool,
            top_confidence=analysis.top_candidate.confidence,
            confidence_threshold=self.CONFIDENCE_THRESHOLD,
            determination="No intent passed the minimum confidence threshold",
        )
        raise ValueError("Intent cannot be validated with the current level of confidence. Please clarify the task.")
#detecting multi intent
    def _multi_intents(self, tool_scores: list[ToolScore]) -> bool:
        return sum(1 for tool_score in tool_scores if tool_score.intent_detected) >= self.MULTI_INTENT_THRESHOLD

    def _tool_dict(self, tool_score: ToolScore) -> dict[str, Any]:
        return {
            "tool": tool_score.tool,
            "confidence": tool_score.confidence,
            "signals": tool_score.signals,
            "reason": tool_score.reason,
            "intent_detected": tool_score.intent_detected,
        }
