from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.user import UserResponse
from app.models.event_staff import StaffRole


class EventBase(BaseModel):
    name: str = Field(max_length=255, description="Tên sự kiện")
    description: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên sự kiện")
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Tên sự kiện không được để trống")
            return v_stripped
        return v


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


class EventDetailResponse(EventResponse):
    role: StaffRole
