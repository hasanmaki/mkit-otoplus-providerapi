"""services digipos related."""

import httpx
from loguru import logger

from src.config.settings import DigiposConfig
from src.schemas.base_response import ApiResponse
from src.schemas.sch_digipos import ResponseBalance
from src.services.clients.base_client import BaseApiClient
from src.services.utils.response_utils import response_as_dict


class ServiceDigiposAccount(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig) -> None:
        super().__init__(client, config)
        self.config: DigiposConfig = config
        self.response_type = config.response.type
        self.log_dgp = logger.bind(name="ServiceDigiposAccount")

    async def _call_and_log(
        self, endpoint: str, params: dict, response_model: type = ApiResponse
    ):
        """Call API, log raw response + headers + meta, normalize, return Pydantic model"""
        raw_response = await self.cst_get(endpoint, params=params)

        # Log lengkap
        self.log_dgp.debug(
            "Raw response captured",
            url=str(raw_response.request.url),
            method=raw_response.request.method,
            status_code=raw_response.status_code,
            headers=dict(raw_response.headers),
            elapsed_ms=raw_response.elapsed.total_seconds() * 1000,
            body=raw_response.text,
        )

        dict_response = response_as_dict(raw_response)
        return response_model(**dict_response)

    async def get_login(self) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.login,
            {"username": self.config.username, "password": self.config.password},
            ApiResponse,
        )

    async def get_verify_otp(self, otp: str) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.verify_otp,
            {"username": self.config.username, "otp": otp},
            ApiResponse,
        )

    async def get_balance(self) -> ResponseBalance:
        return await self._call_and_log(
            self.config.endpoints.balance,
            {"username": self.config.username},
            ResponseBalance,
        )

    async def get_profile(self) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.profile,
            {"username": self.config.username},
            ApiResponse,
        )

    async def get_list_va(self) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.list_va,
            {"username": self.config.username},
            ApiResponse,
        )

    async def get_rewardsummary(self) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.reward,
            {"username": self.config.username},
            ApiResponse,
        )

    async def get_banner(self) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.banner,
            {"username": self.config.username},
            ApiResponse,
        )

    async def get_logout(self) -> ApiResponse:
        return await self._call_and_log(
            self.config.endpoints.logout,
            {"username": self.config.username},
            ApiResponse,
        )
