from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import TokenData

# Khai báo đường dẫn cấp token để hiển thị nút Authorize trên Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    # đọc user từ JWT.

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token xác thực không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã Token với Secret Key và Algorithm đã cấu hình
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id_str), email=email, role=UserRole(role) if role else None)
    except (JWTError, ValueError):
        # Lỗi nghiệp vụ (Xử lý lỗi token hết hạn/sai)
        raise credentials_exception

    # Lấy thông tin user từ cơ sở dữ liệu dựa trên user_id thu được từ Token
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    # Kiểm tra người dùng hiện tại có ở trạng thái hoạt động (is_active=True) không.
    if not current_user.is_active:
        # Lỗi nghiệp vụ (Tài khoản không hoạt động)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản người dùng đã bị vô hiệu hóa."
        )
    return current_user

def require_roles(*allowed_roles: UserRole) -> Callable:

    # Phân quyền cơ bản USER/ADMIN
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            # Lỗi nghiệp vụ (Không đủ quyền hạn truy cập)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện thao tác này."
            )
        return current_user
    return role_checker
