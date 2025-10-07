from enum import StrEnum
from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel

T = TypeVar("T")


class ParsedStatus(StrEnum):
    """Status hasil parsing data."""

    OK = "OK"
    ERROR = "ERROR"
    FORWARD = "FORWARD"


class ApiResponseProcessor[T](BaseModel):
    """Model output akhir, siap untuk encoding."""

    status_code: int
    url: str
    meta: dict[str, Any]
    parsed: ParsedStatus
    data: T  # Bisa DGResBalance (OK) atau dict[str, Any] (FORWARD/ERROR)


class DGResBalance(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


class ApiBalanceResponse(ApiResponseProcessor[DGResBalance]):
    """Digunakan saat parsing sukses (parsed=OK). Data = DGResBalance."""

    parsed: ParsedStatus = ParsedStatus.OK  # Set default agar jelas


class ApiFailedParseResponse(ApiResponseProcessor[dict[str, Any]]):
    """Digunakan saat parsing gagal/forward (parsed=FORWARD/ERROR). Data = dict[str, Any]."""


class DigiposParserService:
    def __init__(self, raw_dict: dict, base_model: BaseModel) -> None:
        self.base_model = base_model
        self.raw_dict = raw_dict
        self.logger = logger.bind(service="Digipos Parser Service")

    def parse_balance(self) -> ApiResponseProcessor[DGResBalance]:
        try:
            validated_data = self.base_model(**self.raw_dict)
            return ApiBalanceResponse(
                status_code=self.raw_dict.get("status_code", 500),
                url=self.raw_dict.get("url", "validation_failed"),
                meta=self.raw_dict.get("meta", {}),
                parsed=ParsedStatus.OK,
                data=validated_data,
            )
        except
