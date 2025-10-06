from pydantic import BaseModel, Field, HttpUrl

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


class DigiposEndpoints(BaseModel):
    login: str = Field(default="add_account")
    verify_otp: str = Field(default="add_account_otp")
    balance: str = Field(default="balance")
    profile: str = Field(default="profile")
    list_va: str = Field(default="list_va")
    logout: str = Field(default="logout")
    reward: str = Field(default="reward_summary")
    banner: str = Field(default="banner")
    sim_status: str = Field(default="sim_status")


class SimStatus(BaseModel):
    sim_status: str


class DigiposConfig(ApiBaseConfig):
    debug: bool = Field(default=False)
    username: str
    password: str
    pin: str
    endpoints: DigiposEndpoints = Field(default_factory=DigiposEndpoints)


class IsimpleConfig(ApiBaseConfig):
    msisdn: str
    pin: str
