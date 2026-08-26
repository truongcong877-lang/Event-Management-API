from sqlalchemy.orm import Session

from app.core.exceptions import bad_request, unauthorized
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserLogin, UserRegister


def register_user(db: Session, user_in: UserRegister) -> User:
    # đăng ký tài khoản
    if db.query(User).filter(User.email == user_in.email).first():
        raise bad_request("Email đã được đăng ký trong hệ thống.")

    new_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.USER,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, login_data: UserLogin) -> Token:
    # Xác thực email/password và trả về access token nếu hợp lệ
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise unauthorized("Email hoặc mật khẩu không chính xác.")

    if not user.is_active:
        raise bad_request("Tài khoản đã bị khoá")

    access_token = create_access_token(
        subject=user.id,
        extra_claims={"email": user.email, "role": user.role.value},
    )
    return Token(access_token=access_token)
