import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.core.config import settings
from app.routers.health import router as health_router

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "message": exc.detail},
    )


@app.get("/")
def start():
    return {"message": "Chào mừng đến với Server Quản lý Sự kiện (Event API)"}


app.include_router(health_router)
