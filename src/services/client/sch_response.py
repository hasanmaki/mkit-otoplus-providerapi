from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ResponseMessage(StrEnum):
    """Jenis hasil parsing body response."""

    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITIVE"
    EMPTY = "EMPTY"
    ERROR = "ERROR"


class ApiRawResponse(BaseModel):
    url: str
    path: str
    status_code: int
    meta: dict[str, Any] = {}
    data: Any
