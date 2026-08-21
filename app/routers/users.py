from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_active_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("", response_model=List[UserResponse])
def list_users(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc email"),
    is_active: Optional[bool] = Query(
        None, description="Lọc theo trạng thái hoạt động"
    ),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    # Danh sách user (chỉ admin)
    query = db.query(User)

    if search:
        pattern = f"%{search}%"
        query = query.filter(User.full_name.ilike(pattern) | User.email.ilike(pattern))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()
