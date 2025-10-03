"""schmeas for digipos."""

from pydantic import BaseModel

from src.schemas.sch_base import ApiResponseGeneric


class RequestBalance(BaseModel):
    username: str


class BalanceData(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


class ResponseBalance(ApiResponseGeneric[BalanceData]):
    pass
