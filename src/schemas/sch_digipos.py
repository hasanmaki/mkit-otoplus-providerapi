"""schmeas for digipos."""

from typing import Any

from pydantic import BaseModel

from src.schemas.base_response import ApiResponseGeneric


class DGReqUsername(BaseModel):
    username: str


class DGReqUsnPass(DGReqUsername):
    password: str


class DGReqUsnOtp(DGReqUsername):
    otp: str


class RequestBalance(DGReqUsername):
    pass


class BalanceData(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


class ResponseBalance(ApiResponseGeneric[BalanceData]):
    pass


# login
class RequestLogin(DGReqUsername):
    password: str


class LoginData(BaseModel):
    data: Any


class ResponseLogin(ApiResponseGeneric[LoginData]):
    pass
