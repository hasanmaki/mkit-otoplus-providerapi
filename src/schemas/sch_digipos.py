"""schmeas for digipos."""

from pydantic import BaseModel


class RequestBalance(BaseModel):
    username: str


class ResponseBalance(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str
