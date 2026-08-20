from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse
from app.models.event_staff import StaffRole

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

class EventStaffCreate(BaseModel):
    user_id: int
    role: StaffRole = StaffRole.MEMBER

class EventStaffResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    role: StaffRole
    joined_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)