"""One error shape for the whole API: {"error": {"code", "message"}}.

Routers and services raise ApiError; the handlers here turn every error into that shape.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


# Default codes for errors raised by FastAPI itself (e.g. unknown route -> 404).
STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    404: "not_found",
    405: "method_not_allowed",
    413: "too_large",
    415: "unsupported_media_type",
    422: "invalid_input",
    429: "rate_limited",
    503: "unavailable",
}


async def handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(error_body(exc.code, exc.message), status_code=exc.status_code)


async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = STATUS_CODES.get(exc.status_code, "error")
    return JSONResponse(error_body(code, str(exc.detail)), status_code=exc.status_code)


async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Show the first problem in plain words; the full list is noise for the user.
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = f"{field}: {first.get('msg', 'invalid input')}" if field else "Invalid input"
    return JSONResponse(error_body("invalid_input", message), status_code=422)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, handle_api_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
