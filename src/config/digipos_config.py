from pydantic import BaseModel, Field

from src.config.client_config import ClientBaseConfig


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


class DigiposConfig(ClientBaseConfig):
    username: str
    password: str
    pin: str
    endpoints: DigiposEndpoints = Field(default_factory=DigiposEndpoints)
