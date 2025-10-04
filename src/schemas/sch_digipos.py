"""schmeas for digipos."""

from typing import Any

from pydantic import BaseModel

from src.schemas.sch_base import ApiResponseGeneric


class DGUsername(BaseModel):
    username: str


class RequestBalance(DGUsername):
    pass


class BalanceData(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


class ResponseBalance(ApiResponseGeneric[BalanceData]):
    pass


# login
class RequestLogin(DGUsername):
    password: str


class LoginData(BaseModel):
    data: Any


class ResponseLogin(ApiResponseGeneric[LoginData]):
    pass
