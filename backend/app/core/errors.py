from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

class NotFoundError(AppError):
    def __init__(self, message="Data tidak ditemukan", details=None):
        super().__init__("NOT_FOUND", message, 404, details)

class ConflictError(AppError):
    def __init__(self, message="Konflik data", details=None):
        super().__init__("CONFLICT", message, 409, details)

class ValidationError(AppError):
    def __init__(self, message="Validasi gagal", details=None):
        super().__init__("VALIDATION_ERROR", message, 422, details)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={
            "code": exc.code, "message": exc.message, "details": exc.details,
        })
    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={
            "code": "INTERNAL_ERROR", "message": "Terjadi kesalahan internal", "details": None,
        })