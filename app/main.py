from fastapi import FastAPI, status
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.database import engine, Base
import app.models  # Ensure models are loaded before create_all

app = FastAPI(title=settings.PROJECT_NAME)

# Register global exception handlers
register_exception_handlers(app)

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Root"])
def start():
    return {"message": f"Chào mừng đến với {settings.PROJECT_NAME}"}


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": status.HTTP_200_OK,
        "message": "Dịch vụ đang hoạt động bình thường",
    }
