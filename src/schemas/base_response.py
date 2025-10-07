from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ParsedStatus(StrEnum):
    """Status hasil parsing data."""

    OK = "OK"
    ERROR = "ERROR"
    FORWARD = "FORWARD"


class ApiRawResponse(BaseModel):
    """Model untuk memvalidasi struktur dasar respons API eksternal.

    #Model Respons Mentah (Input dari Upstream)
    """

    status_code: int
    url: str
    meta: dict[str, Any]
    message: str  # Kunci utama untuk logika parsing
    data: dict[str, Any]  # Data mentah/belum divalidasi


# --- 2.3 Model Hasil Akhir (Output/Envelope Model) ---
class ApiResponseProcessor[T](BaseModel):
    """Model output akhir, siap untuk encoding."""

    status_code: int
    url: str
    meta: dict[str, Any]
    parsed: ParsedStatus
    data: T  # Bisa DGResBalance (OK) atau dict[str, Any] (FORWARD/ERROR)
