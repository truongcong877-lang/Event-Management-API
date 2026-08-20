from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserRegister) -> User:
        # Tạo tài khoản
        # Kiểm tra xem email đã được đăng ký trong hệ thống chưa
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            # Lỗi nghiệp vụ (Email trùng)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký trong hệ thống.",
            )

        # Mã hóa mật khẩu bằng bcrypt và tạo đối tượng User mới
        db_user = User(
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            full_name=user_in.full_name,
            role=UserRole.USER,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> dict:
        # xác thực email/password và trả access token JWT hợp lệ.
        # Tìm người dùng theo email
        user = db.query(User).filter(User.email == login_data.email).first()

        # Xác thực email tồn tại và mật khẩu khớp với password_hash
        if not user or not verify_password(login_data.password, user.password_hash):
            # Lỗi nghiệp vụ (Đăng nhập sai)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Kiểm tra tài khoản có bị vô hiệu hóa không
        if not user.is_active:
            # Lỗi nghiệp vụ (Tài khoản không hoạt động)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản đã bị vô hiệu hóa.",
            )

        # Tạo JWT Access Token hợp lệ
        access_token = create_access_token(
            subject=user.id, extra_claims={"email": user.email, "role": user.role.value}
        )
        return {"access_token": access_token, "token_type": "bearer"}
