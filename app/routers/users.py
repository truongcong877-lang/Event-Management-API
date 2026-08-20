from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_active_user, require_roles

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
# trả thông tin không có password
    return current_user

@router.get("", response_model=List[UserResponse])
def get_users(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc email"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái hoạt động"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(UserRole.ADMIN))
):
    # Lấy danh sách user (chỉ ADMIN mới có quyền)
    query = db.query(User)
    
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_fmt)) | (User.email.ilike(search_fmt))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
        
    return query.all()
