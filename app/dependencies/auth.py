from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import ( bad_request, unauthorized, forbidden)
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import TokenData

http_bearer = HTTPBearer()


def _decode_token(token: str) -> TokenData:
    # Giải mã JWT và trả về TokenData
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise unauthorized("Token không chứa thông tin người dùng.")
        return TokenData(
            user_id=int(user_id_str),
            email=payload.get("email"),
            role=UserRole(payload.get("role")) if payload.get("role") else None,
        )
    except (JWTError, ValueError):
        raise unauthorized("Token không hợp lệ hoặc đã hết hạn.")


def _get_user_by_id(db: Session, user_id: int) -> User:
    # kiểm tra user trong db
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise unauthorized("Người dùng không tồn tại.")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> User:
    # Lấy user từ JWT Bearer token
    token_data = _decode_token(credentials.credentials)
    return _get_user_by_id(db, token_data.user_id)


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    # kiểm tra (is_active=True)
    if not current_user.is_active:
        raise bad_request("Tài khoản đã bị vô hiệu hóa.")
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    # phân quyền admin
    if current_user.role != UserRole.ADMIN:
        raise forbidden("Yêu cầu quyền ADMIN.")
    return current_user
