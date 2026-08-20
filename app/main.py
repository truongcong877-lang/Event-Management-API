from fastapi import FastAPI, status
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.database import engine, Base
import app.models  # Đảm bảo các model đã được nạp trước khi gọi create_all
from app.routers import auth, users

app = FastAPI(title=settings.PROJECT_NAME)

# Đăng ký các bộ xử lý ngoại lệ toàn cục
register_exception_handlers(app)

# Tạo các bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Đăng ký các router
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/", tags=["Root"])
def start():
    return {"message": f"Chào mừng đến với {settings.PROJECT_NAME}"}


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": status.HTTP_200_OK,
        "message": "Dịch vụ đang hoạt động bình thường",
    }
