from pydantic import BaseModel, Field, HttpUrl, field_validator

default_headers = {
    "User-Agent": "MKIT-Trimmer-API/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


class ApiBaseConfig(BaseModel):
    base_url: HttpUrl
    headers: dict[str, str] = Field(default_headers)
    timeout: int = 10
    http2: bool = Field(default=False)


class APiBaseResponse(BaseModel):
    type: str | None = Field(default="text")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v not in ["json", "text"]:
            raise ValueError("type must be 'json' or 'text'")
        return v


class DigiposEndpoints(BaseModel):
    login: str
    verify_otp: str
    balance: str
    profile: str
    list_va: str
    logout: str
    reward: str
    banner: str
    sim_status: str


class DigiposConfig(ApiBaseConfig):
    username: str
    password: str
    pin: str
    response: APiBaseResponse
    endpoints: DigiposEndpoints


class IsimpleConfig(ApiBaseConfig):
    msisdn: str
    pin: str
