from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse
from app.models.event_task import TaskStatus, TaskPriority

class EventTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class EventTaskCreate(EventTaskBase):
    assignee_id: Optional[int] = None

class EventTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    status: TaskStatus
    assignee_id: Optional[int] = None
    created_at: datetime
    assignee: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)