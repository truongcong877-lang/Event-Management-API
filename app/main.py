from fastapi import FastAPI, status
from app.db.database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def start():
    return {"message": "Chào mừng đến với Server Quản lý Sự kiện (Event API)"}


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": status.HTTP_200_OK,
        "message": "Dịch vụ đang hoạt động bình thường",
    }
