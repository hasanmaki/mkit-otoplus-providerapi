"""services digipos related."""

import httpx

from src.config.settings import DigiposConfig
from src.schemas.sch_base import ApiResponse
from src.services.clients.base import BaseApiClient
from src.services.utils.response_utils import response_as_dict


class ServiceDigipos(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig) -> None:
        super().__init__(client, config)
        self.config: DigiposConfig = config
        self.response_type = config.response.type

    async def get_login(self) -> ApiResponse:
        """Get login from Digipos."""
        endpoint = self.config.endpoints.login
        params = {"username": self.config.username, "password": self.config.password}
        raw_response = await self.cst_get(endpoint, params=params)
        dict_response = response_as_dict(raw_response)
        return ApiResponse(**dict_response)

    async def get_verify_otp(self, otp: str) -> ApiResponse:
        """Verify OTP for Digipos login."""
        endpoint = self.config.endpoints.verify_otp
        params = {"username": self.config.username, "otp": otp}
        raw_response = await self.cst_get(endpoint, params=params)
        dict_response = response_as_dict(raw_response)
        return ApiResponse(**dict_response)

    async def get_balance(self) -> ApiResponse:
        """Get balance from Digipos."""
        endpoint = self.config.endpoints.balance
        params = {"username": self.config.username}
        raw_response = await self.cst_get(endpoint, params=params)
        dict_response = response_as_dict(raw_response)
        return ApiResponse(**dict_response)

    async def get_profile(self) -> ApiResponse:
        """Get profile from Digipos."""
        endpoint = self.config.endpoints.profile
        params = {"username": self.config.username}
        raw_response = await self.cst_get(endpoint, params=params)
        return ApiResponse(**response_as_dict(raw_response))

    async def get_list_va(self) -> ApiResponse:
        """Get list VA from Digipos."""
        endpoint = self.config.endpoints.list_va
        params = {"username": self.config.username}
        raw_response = await self.cst_get(endpoint, params=params)
        return ApiResponse(**response_as_dict(raw_response))

    async def get_rewardsummary(self) -> ApiResponse:
        """Get reward summary from Digipos."""
        endpoint = self.config.endpoints.reward
        params = {"username": self.config.username}
        raw_response = await self.cst_get(endpoint, params=params)
        return ApiResponse(**response_as_dict(raw_response))

    async def banner(self) -> ApiResponse:
        """Get banner from Digipos."""
        endpoint = self.config.endpoints.banner
        params = {"username": self.config.username}
        raw_response = await self.cst_get(endpoint, params=params)
        return ApiResponse(**response_as_dict(raw_response))

    async def get_logout(self) -> ApiResponse:
        """Logout from Digipos."""
        endpoint = self.config.endpoints.logout
        params = {"username": self.config.username}
        raw_response = await self.cst_get(endpoint, params=params)
        return ApiResponse(**response_as_dict(raw_response))
