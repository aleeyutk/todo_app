from datetime import datetime, date
import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models import Priority, Status


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=120, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority (LOW, MEDIUM, HIGH)")
    status: Status = Field(default=Status.PENDING, description="Task status (PENDING, IN_PROGRESS, COMPLETED)")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    category: Optional[str] = Field(None, max_length=50, description="Category / tag for organization")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v_stripped = v.strip()
        if len(v_stripped) < 3:
            raise ValueError("Title must be at least 3 characters long after trimming")
        return v_stripped

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, v):
            raise ValueError("Due date must be in YYYY-MM-DD format")
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Invalid calendar date for due date")
        return v


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    due_date: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if len(v_stripped) < 3:
                raise ValueError("Title must be at least 3 characters long after trimming")
            return v_stripped
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, v):
            raise ValueError("Due date must be in YYYY-MM-DD format")
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Invalid calendar date for due date")
        return v


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120, description="Note title")
    content: str = Field(..., min_length=1, max_length=5000, description="Note body content")
    tags: Optional[str] = Field(None, max_length=255, description="Comma-separated tags")
    task_id: Optional[int] = Field(None, description="Optional associated task ID")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Title cannot be empty")
        return v_stripped

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Content cannot be empty")
        return v_stripped


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    tags: Optional[str] = Field(None, max_length=255)
    task_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Title cannot be empty")
            return v_stripped
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Content cannot be empty")
            return v_stripped
        return v


class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    total_notes: int
    completion_rate_percentage: float


class BackupData(BaseModel):
    version: str = "1.0"
    exported_at: str
    tasks: List[TaskResponse]
    notes: List[NoteResponse]
