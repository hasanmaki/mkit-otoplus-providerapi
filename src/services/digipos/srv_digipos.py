"""services digipos related."""

import httpx

from src.config.settings import DigiposConfig
from src.services.clients.base import BaseApiClient
from src.services.utils.response_utils import response_as_dict


class ServiceDigipos(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig) -> None:
        super().__init__(client, config)
        self.config: DigiposConfig = config
        self.response_type = config.response.type

    async def get_login(self):
        """get login from digipos."""
        endpoint: str = self.config.endpoints.login
        params = {
            "username": self.config.username,
            "password": self.config.password,
        }
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    async def get_verify_otp(self, otp: str):
        """get verify otp from digipos."""
        endpoint: str = self.config.endpoints.verify_otp
        params = {"username": self.config.username, "otp": otp}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    # delete account not inserted here, jumpt to balance
    async def get_balance(self):
        """get balance from digipos."""
        endpoint = self.config.endpoints.balance
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    async def get_profile(self):
        """get profile from digipos."""
        endpoint: str = self.config.endpoints.profile
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    async def get_list_va(self):
        """get list va from digipos."""
        endpoint: str = self.config.endpoints.list_va
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    async def get_rewardsummary(self):
        """get reward summary from digipos."""
        endpoint: str = self.config.endpoints.reward
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    async def banner(self):
        """get banner from digipos."""
        endpoint: str = self.config.endpoints.banner
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)

    async def get_logout(self):
        """get logout from digipos."""
        endpoint: str = self.config.endpoints.logout
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response_as_dict(response)
