from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from loguru import logger


class AppExceptionError(Exception):
    """Base exception untuk semua klien dan aplikasi."""

    default_message: str = "An application error occurred."
    status_code: int = 400
    context: dict[str, Any]

    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
        status_code: int | None = None,
    ):
        self.message = message or self.default_message
        self.context = context or {}
        self.__cause__ = cause
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Representasi yang ramah JSON."""
        data: dict[str, Any] = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.context:
            data["context"] = self.context.copy()
        return data


# Handler Pengecualian Global
async def global_exception_handler(request: Request, exc: AppExceptionError):
    """Handler dinamis untuk AppExceptionError (mendukung JSON dan TEXT)."""

    # --- 1. Logging Terpusat ---
    log_context = {
        "path": str(request.url.path),
        "method": request.method,
        "client_ip": request.client.host if request.client else None,
        "status_code_resp": exc.status_code,
        "error_context": exc.context,
    }

    if exc.__cause__:
        logger.bind(**log_context).error(
            f"{exc.message} | Caused by: {exc.__cause__}", exception=exc.__cause__
        )
    else:
        logger.bind(**log_context).error(exc.message)

    response_format = request.headers.get(
        "X-Response-Format"
    ) or request.query_params.get("format", "json")

    if response_format.lower() == "text":
        text = f"[{exc.__class__.__name__}] {exc.message}"
        if exc.context:
            text += f" | Context: {exc.context}"
        return PlainTextResponse(text, status_code=exc.status_code)

    return JSONResponse(content=exc.to_dict(), status_code=exc.status_code)


class HttpResponseError(AppExceptionError):
    """Pengecualian yang dimunculkan untuk kode status HTTP 4xx/5xx."""

    default_message: str = "Error response from external service."
    status_code: int = 502  # Bad Gateway / Pihak ketiga memberikan error


class HTTPConnectionError(AppExceptionError):
    """Pengecualian yang dimunculkan untuk kesalahan koneksi/timeout."""

    default_message: str = "Service unavailable: Failed to connect to external service."
    status_code: int = 503  # Service Unavailable


class AuthenticationError(AppExceptionError):
    """Pengecualian untuk kegagalan otentikasi."""

    default_message: str = "Authentication required or invalid credentials."
    status_code: int = 401


class ApiCredentialsError(AuthenticationError):
    """Pengecualian untuk kredensial API yang tidak valid atau hilang."""

    default_message: str = "Invalid or missing API credentials."
    status_code: int = 401


class ExternalAPIError(HttpResponseError):
    """Pengecualian untuk kesalahan yang diterima dari API eksternal."""

    default_message: str = "External API returned an error."
    status_code: int = 502
