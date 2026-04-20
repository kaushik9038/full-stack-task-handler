"""Pydantic schemas for request and response payloads."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    task: str = Field(..., min_length=1, description="Natural language task to execute")


class ExecutionStep(BaseModel):
    stage: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    id: int
    task: str
    final_output: str
    selected_tool: str
    tools_used: list[str]
    execution_steps: list[ExecutionStep]
    timestamp: datetime

    class Config:
        from_attributes = True
