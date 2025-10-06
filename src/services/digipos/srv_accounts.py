# src/services/digipos/service_account.py
from typing import Any, Dict

import httpx
from loguru import logger

from src.config.settings import AppSettings, DigiposConfig
from src.services.clients.base_client import BaseApiClient
from src.services.utils.output_utils import encode_response_upstream
from src.services.utils.response_utils import response_to_normalized_dict


class ServiceDigiposAccount(BaseApiClient):
    """Service untuk komunikasi ke Digipos API (balance, profile, login)."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        config: DigiposConfig,
        settings: AppSettings,
    ) -> None:
        super().__init__(client, config)
        self.settings = settings
        self.config = config
        self.log = logger.bind(service="digipos_account")

    async def _call_api_core(self, endpoint: str, params: dict) -> Dict[str, Any]:
        """
        Eksekusi HTTP call ke endpoint → normalisasi ke dict
        """
        raw_response = await self.get(endpoint, params=params)
        return response_to_normalized_dict(
            response=raw_response, debug=self.settings.application.debug
        )

    async def _return(self, data: Dict[str, Any]) -> str | Dict[str, Any]:
        """
        Tentukan output final:
        - dict → kalau debug (developer mode)
        - string → kalau production (encoded)
        """
        # if self.settings.application.debug:
        #     return data
        return encode_response_upstream(data)

    async def get_balance(self) -> dict | str:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.balance, params)
        return await self._return(data)

    async def get_profile(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.profile, params)
        return await self._return(data)

    async def login(self) -> str | Dict[str, Any]:
        params = {
            "username": self.config.username,
            "password": self.config.password,
        }
        data = await self._call_api_core(self.config.endpoints.login, params)
        return await self._return(data)

    async def verify_otp(self, otp: str) -> str | Dict[str, Any]:
        params = {
            "username": self.config.username,
            "otp": otp,
        }
        data = await self._call_api_core(self.config.endpoints.verify_otp, params)
        return await self._return(data)

    async def logout(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.logout, params)
        return await self._return(data)

    async def list_va(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.list_va, params)
        return await self._return(data)

    async def reward(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.reward, params)
        return await self._return(data)

    async def banner(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.banner, params)
        return await self._return(data)
