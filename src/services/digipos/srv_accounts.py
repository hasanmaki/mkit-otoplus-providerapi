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
            response=raw_response, debug=self.config.debug
        )

    async def get_balance(self) -> dict | str:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.balance, params)
        return encode_response_upstream(data)

    async def get_profile(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.profile, params)
        return encode_response_upstream(data)

    async def login(self) -> str | Dict[str, Any]:
        params = {
            "username": self.config.username,
            "password": self.config.password,
        }
        data = await self._call_api_core(self.config.endpoints.login, params)
        return encode_response_upstream(data)

    async def verify_otp(self, otp: str) -> str | Dict[str, Any]:
        params = {
            "username": self.config.username,
            "otp": otp,
        }
        data = await self._call_api_core(self.config.endpoints.verify_otp, params)
        return encode_response_upstream(data)

    async def logout(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.logout, params)
        return encode_response_upstream(data)

    async def list_va(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.list_va, params)
        return encode_response_upstream(data)

    async def reward(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.reward, params)
        return encode_response_upstream(data)

    async def banner(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_api_core(self.config.endpoints.banner, params)
        return encode_response_upstream(data)
