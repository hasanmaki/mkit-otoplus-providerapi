from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponseGeneric[T](BaseModel):
    """base schemas untuk semua response dari api yang sudah di standardisasi."""

    status_code: int
    content_length: int | None
    meta: dict[str, Any]
    data: T
