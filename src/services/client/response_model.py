from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)


class ResponseMessage(StrEnum):
    """Jenis hasil parsing body response dari raw api parser."""

    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITIVE"
    EMPTY = "EMPTY"
    ERROR = "ERROR Parse"


class CleanAndParseStatus(StrEnum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    UNPROCESSED = "UNPROCESSED"


class ApiShared(BaseModel):
    """commons Field In Out Response."""

    status_code: int = Field(description="status code dari API / Layanan.")
    url: str = Field(description="urlapi tanpa query(sensitive data)")
    debug: bool = Field(description="debug mode tracking")
    meta: dict[str, Any] | None = Field(
        description="jika debug mode, ini akan berisi header lengkap dan data lainya"
    )


class ApiResponseIN(ApiShared):
    """Raw response yang di berikan oleh API."""

    raw_data: Any = Field(
        description="pesan raw dari api yang akan di proses dan di replace oleh parser."
    )


class ApiResponseOUT[T](ApiShared, BaseModel):
    """standarisai output untuk downstream.

    data akan terisi oleh hasil preprosesing / raw. jika gagal parse.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )
    parse: CleanAndParseStatus = Field(description="informasi status parsing")
    cleaned_data: T | None = Field(description="data yang sudah di clean dan di parse")
    description: str | None = Field(
        description="placeholder pesan error / informasi lain nya."
    )


class APResponseOutError(ApiResponseOUT[None]):
    pass
