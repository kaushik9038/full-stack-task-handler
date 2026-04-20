"""Task API routes."""

import json
from datetime import timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agent.controller import TaskController, TaskRejectedError
from app.db.models import TaskRecord
from app.db.schemas import TaskCreate, TaskResponse
from app.db.session import get_db


router = APIRouter()


class TaskService:
    def __init__(self, db: Session, controller: Optional[TaskController] = None) -> None:
        self.db = db
        self.controller = controller or TaskController()

    def create_task(self, task_text: str) -> TaskResponse:
        try:
            task_result = self.controller.run_task(task_text)
        except TaskRejectedError as exc:
            record = TaskRecord(
                task=task_text,
                final_output=str(exc),
                selected_tool=exc.selected_tool,
                tools_used_json=json.dumps(exc.tools_used),
                execution_steps_json=json.dumps(exc.execution_steps),
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            raise

        record = TaskRecord(
            task=task_result["task"],
            final_output=task_result["final_output"],
            selected_tool=task_result["selected_tool"],
            tools_used_json=json.dumps(task_result["tools_used"]),
            execution_steps_json=json.dumps([step.model_dump() for step in task_result["execution_steps"]]),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_response(record)

    def list_tasks(self) -> list[TaskResponse]:
        records = self.db.query(TaskRecord).order_by(TaskRecord.id.desc()).all()
        return [self._to_response(record) for record in records]

    def get_task(self, task_id: int) -> Optional[TaskResponse]:
        record = self.db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
        return self._to_response(record) if record else None

    def _to_response(self, record: TaskRecord) -> TaskResponse:
        created_at = record.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return TaskResponse(
            id=record.id,
            task=record.task,
            final_output=record.final_output,
            selected_tool=record.selected_tool,
            tools_used=json.loads(record.tools_used_json),
            execution_steps=json.loads(record.execution_steps_json),
            timestamp=created_at,
        )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    service = TaskService(db)
    try:
        return service.create_task(payload.task.strip())
    except TaskRejectedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)) -> list[TaskResponse]:
    service = TaskService(db)
    return service.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
