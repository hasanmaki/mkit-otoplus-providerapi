from typing import Any


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
        data: dict[str, Any] = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.context:
            data["context"] = self.context.copy()
        return data


# --- HTTP / Connection Errors ---
class HttpResponseError(AppExceptionError):
    """Error untuk kode status HTTP 4xx/5xx."""

    default_message: str = "Error response from external service."
    status_code: int = 502


class HTTPConnectionError(AppExceptionError):
    """Error saat koneksi/timeout gagal."""

    default_message: str = "Service unavailable: Failed to connect to external service."
    status_code: int = 503


# --- Authentication / Credential Errors ---
class AuthenticationError(AppExceptionError):
    """Error otentikasi umum."""

    default_message: str = "Authentication required or invalid credentials."
    status_code: int = 401


class ApiCredentialsError(AuthenticationError):
    """Error kredensial API hilang atau tidak valid."""

    default_message: str = "Invalid or missing API credentials."


# --- External API Errors ---
class ExternalAPIError(HttpResponseError):
    """Error dari API eksternal."""

    default_message: str = "External API returned an error."
