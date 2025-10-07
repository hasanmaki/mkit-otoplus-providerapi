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
