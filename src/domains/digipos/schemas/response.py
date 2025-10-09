"""schemas for parsing or any necessary operations."""

from pydantic import BaseModel
from typing_extensions import TypeVar

T = TypeVar("T", bound=BaseModel)


class BalanceResponse(BaseModel):
    pass


class LoginResponse(BaseModel):
    pass


class verify_otp(BaseModel):
    pass
