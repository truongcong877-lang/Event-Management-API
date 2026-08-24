from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.event_task import TaskStatus, TaskPriority
from app.schemas.user import UserResponse


class EventTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class EventTaskCreate(EventTaskBase):
    status: Optional[TaskStatus] = TaskStatus.TODO
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tiêu đề không được để trống")
        return v

class EventTaskUpdate(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Tiêu đề không được để trống")
        return v

    model_config = ConfigDict(str_strip_whitespace=True)

class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    status: TaskStatus
    assignee_id: Optional[int] = None
    created_at: datetime
    assignee: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)