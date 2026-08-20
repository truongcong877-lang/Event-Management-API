from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)