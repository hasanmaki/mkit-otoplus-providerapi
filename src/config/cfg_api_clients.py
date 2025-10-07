from pydantic import BaseModel, Field, HttpUrl

default_headers = {
    "User-Agent": "MKIT-Trimmer-API/1.0",
    "Accept": "application/json",
}


class ClientRetry(BaseModel):
    total: int = 5
    backoff_factor: float = 0.5
    status_forcelist: list[int] = [429, 500, 502, 503, 504]
    allowed_methods: list[str] = ["GET", "POST"]


class ClientLimits(BaseModel):
    max_keepalive_connections: int = 100
    max_connections: int = 100
    keepalive_expiry: int = 300


class ApiBaseConfig(BaseModel):
    name: str
    base_url: HttpUrl
    headers: dict[str, str] = Field(default_headers)
    timeout: int = 10
    http2: bool = Field(default=False)
    debug: bool = Field(default=False)
    retry: ClientRetry = Field(default_factory=ClientRetry)
    limits: ClientLimits = Field(default_factory=ClientLimits)


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
    username: str
    password: str
    pin: str
    endpoints: DigiposEndpoints = Field(default_factory=DigiposEndpoints)


class IsimpleConfig(ApiBaseConfig):
    msisdn: str
    pin: str
