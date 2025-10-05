from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponseGeneric[T](BaseModel):
    """base schemas untuk semua response dari api yang sudah di standardisasi."""

    status_code: int
    meta: dict[str, Any] | None
    data: T

    model_config = {"extra": "allow"}


class ApiResponse(BaseModel):
    status_code_target: int
    meta: dict[str, Any] | None
    data: Any

    model_config = {"extra": "allow"}
