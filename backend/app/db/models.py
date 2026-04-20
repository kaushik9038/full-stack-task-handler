"""SQLAlchemy models for persisted task data."""

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
