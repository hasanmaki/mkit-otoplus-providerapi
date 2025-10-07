"""schmeas for digipos."""

from pydantic import BaseModel


class DGReqUsername(BaseModel):
    username: str


class DGReqUsnPass(DGReqUsername):
    password: str


class DGReqUsnOtp(DGReqUsername):
    otp: str


class DGReqSimStatus(DGReqUsername):
    to: str


class DGResBalance(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str
