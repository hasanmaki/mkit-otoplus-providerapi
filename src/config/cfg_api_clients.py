from pydantic import BaseModel, Field

default_headers = {
    "User-Agent": "MKIT-Trimmer-API/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


class ApiBaseConfig(BaseModel):
    base_url: str
    headers: dict[str, str] = Field(default_headers)
    timeout: int = 10
    http2: bool = Field(default=False)


class DigiposConfig(ApiBaseConfig):
    username: str
    password: str
    pin: str
