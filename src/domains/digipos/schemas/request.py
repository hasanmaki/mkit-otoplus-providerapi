from pydantic import BaseModel, ConfigDict, Field


class BaseRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )
    debug: bool = Field(default=False)
    text: bool = Field(default=True)


class ReqUsername(BaseRequest):
    username: str


class ReqUsnPassword(ReqUsername):
    password: str


class ReqUsnOtp(ReqUsername):
    otp: str
