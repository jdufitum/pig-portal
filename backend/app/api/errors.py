from __future__ import annotations

from fastapi import Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


def error_payload(code: str, message: str, details: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"error_code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return payload


def register_error_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content=error_payload("validation_error", "Validation failed", exc.errors()))

    @app.exception_handler(ValidationError)
    async def handle_validation(request: Request, exc: ValidationError):
        return JSONResponse(status_code=422, content=error_payload("validation_error", "Validation failed", exc.errors()))

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        return JSONResponse(status_code=409, content=error_payload("integrity_error", "Integrity constraint violated"))

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        # Preserve original status code, wrap message in consistent envelope
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(status_code=exc.status_code, content=error_payload("http_error", message))

