"""Task database record and API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.db.session import Base


class TaskRecord(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    final_output = Column(Text, nullable=False)
    selected_tool = Column(String(100), nullable=False)
    tools_used_json = Column(Text, nullable=False)
    execution_steps_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


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
