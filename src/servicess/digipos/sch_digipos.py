"""schmeas for digipos."""

from pydantic import BaseModel, Field


class DGReqUsername(BaseModel):
    username: str
    debug: bool = Field(default=False)
    text: bool = Field(default=True)


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
