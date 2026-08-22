from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class AppException(Exception):
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}

class NotFoundException(AppException):
    def __init__(self, message: str = "Tài nguyên không tồn tại", details: dict = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, details=details)

class BadRequestException(AppException):
    def __init__(self, message: str = "Yêu cầu không hợp lệ", details: dict = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message, details=details)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Bạn không có quyền truy cập", details: dict = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message, details=details)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Chưa xác thực hoặc phiên làm việc đã hết hạn", details: dict = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message, details=details)

def create_error_response(status_code: int, message: str, details: dict = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status_code": status_code,
            "message": message,
            "details": details or {}
        }
    )

from fastapi.encoders import jsonable_encoder

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return create_error_response(exc.status_code, exc.message, exc.details)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        message = str(exc.detail) if exc.detail else "Lỗi HTTP"
        return create_error_response(exc.status_code, message)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Dữ liệu đầu vào không hợp lệ",
            details={"errors": jsonable_encoder(exc.errors())}
        )

