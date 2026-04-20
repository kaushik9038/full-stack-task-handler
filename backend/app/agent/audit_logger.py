"""logs execution steps"""

from typing import Any

from app.db.tasks import ExecutionStep


class AuditLogger:
    def __init__(self) -> None:
        self._steps: list[ExecutionStep] = []

    def record_step(self, stage: str, message: str, **details: Any) -> None:
        self._steps.append(ExecutionStep(stage=stage, message=message, details=details))

    def export_steps(self) -> list[ExecutionStep]:
        return self._steps.copy()
