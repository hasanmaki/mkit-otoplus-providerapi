from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponseGeneric[T](BaseModel):
    """base schemas untuk semua response dari api yang sudah di standardisasi.

    next kita akan bermain dsini biar enak.
    """

    api_status_code: int
    meta: dict[str, Any] | None
    data: T

    model_config = {"extra": "allow"}


class ApiResponse(BaseModel):
    """api response standard pertama.

    nanti refactor kalo calm"""

    api_status_code: int
    meta: dict[str, Any] | None
    data: Any

    model_config = {"extra": "allow"}
