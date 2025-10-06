# src/services/digipos/service_account.py
from typing import Any, Dict

import httpx
from loguru import logger

from src.config.settings import DigiposConfig
from src.services.clients.base_client import BaseApiClient
from src.services.utils.output_utils import encode_response_upstream


class ServiceDigiposAccount(BaseApiClient):
    """Service untuk komunikasi ke Digipos API (balance, profile, login)."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        config: DigiposConfig,
    ) -> None:
        super().__init__(client, config)
        self.config = config
        self.log = logger.bind(service="digipos_account")

    async def get_balance(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.balance, params=params
        )
        return encode_response_upstream(data)

    async def get_profile(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.profile, params=params
        )
        return encode_response_upstream(data)

    async def login(self) -> str | Dict[str, Any]:
        params = {
            "username": self.config.username,
            "password": self.config.password,
        }
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.login, params=params
        )
        return encode_response_upstream(data)

    async def verify_otp(self, otp: str) -> str | Dict[str, Any]:
        params = {
            "username": self.config.username,
            "otp": otp,
        }
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.verify_otp, params=params
        )
        return encode_response_upstream(data)

    async def logout(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.logout, params=params
        )
        return encode_response_upstream(data)

    async def list_va(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.list_va, params=params
        )
        return encode_response_upstream(data)

    async def reward(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.reward, params=params
        )
        return encode_response_upstream(data)

    async def banner(self) -> str | Dict[str, Any]:
        params = {"username": self.config.username}
        data = await self._call_and_normalize(
            method="GET", endpoint=self.config.endpoints.banner, params=params
        )
        return encode_response_upstream(data)
