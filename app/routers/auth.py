from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Đăng ký tài khoản
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_user(db=db, user_in=user_in)

# Đăng nhập
@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return AuthService.authenticate_user(db=db, login_data=login_data)

# Đăng nhập trên Swagger
@router.post("/login/swagger", response_model=Token, include_in_schema=False)
def login_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return AuthService.authenticate_user(db=db, login_data=login_data)
