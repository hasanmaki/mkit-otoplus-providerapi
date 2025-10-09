from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ResponseType(StrEnum):
    """Jenis hasil parsing body response dari raw api parser."""

    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITIVE"
    EMPTY = "EMPTY"
    ERROR = "ERROR Parse"


@dataclass
class ApiResponseIN:
    """Raw API response in neutral format."""

    status_code: int
    url: str
    path: str
    raw_data: Any
    meta: dict | None = None
    debug: bool = False

    @property
    def response_type(self) -> str | None:
        """Returns the response type from meta data."""
        return self.meta.get("response_type") if self.meta else None

    @property
    def description(self) -> str | None:
        """Returns the description from meta data."""
        return self.meta.get("description") if self.meta else None

    @property
    def is_error(self) -> bool:
        """Indicates if the response is an error based on response type."""
        return self.response_type == ResponseType.ERROR

    @property
    def is_ok(self) -> bool:
        """Indicates if the response is successful (not an error and status code < 400)."""
        return not self.is_error and self.status_code < 400
