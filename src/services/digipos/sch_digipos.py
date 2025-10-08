"""schmeas for digipos."""

from pydantic import BaseModel, Field


class DGReqUsername(BaseModel):
    username: str
    debug: bool = Field(default=False)


class DGReqUsnPass(DGReqUsername):
    password: str


class DGReqUsnOtp(DGReqUsername):
    otp: str


class DGReqSimStatus(DGReqUsername):
    to: str


class DGResBalance(BaseModel):
    ngrs: dict[str, str] | None
    linkaja: str | None
    finpay: str | None
