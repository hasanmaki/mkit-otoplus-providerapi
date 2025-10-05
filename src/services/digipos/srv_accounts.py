import json
from typing import Any, Dict

import httpx
from loguru import logger

from src.config.settings import AppSettings, DigiposConfig
from src.services.clients.base_client import BaseApiClient
from src.services.utils.response_utils import (
    response_upstream_to_dict as response_as_dict,
)


def _format_value(value: Any) -> str:
    """Convert dict/list ke string tanpa banyak kutip biar regex-friendly."""
    if isinstance(value, (dict, list)):
        json_str = json.dumps(value, ensure_ascii=False)
        # hilangkan tanda kutip dari key dan value yang simple
        return json_str.replace('"', "").replace("'", "")
    return str(value)


def encode_response_upstream(response_dict: Dict[str, Any]) -> str:
    """
    Encode response upstream ke format:
    api_status_code=200&meta={url:http...,method:GET}&data={...}
    """
    parts = []
    for key, value in response_dict.items():
        value_str = _format_value(value)
        parts.append(f"{key}={value_str}")
    return "&".join(parts)


class ServiceDigiposAccount(BaseApiClient):
    """Service untuk komunikasi ke Digipos API (contoh: balance, login, dsb)."""

    def __init__(
        self, client: httpx.AsyncClient, config: DigiposConfig, settings: AppSettings
    ) -> None:
        super().__init__(client, config)
        self.config = config
        self.settings = settings
        self.log = logger.bind(service="digipos_account")

    async def _call_api_core(self, endpoint: str, params: dict) -> str | Dict[str, Any]:
        """
        Fungsi inti: call API, logging, dan kembalikan dict atau plain text.
        """
        raw_response = await self.cst_get(endpoint, params=params)

        self.log.debug(
            "Raw response captured",
            url=str(raw_response.request.url),
            method=raw_response.request.method,
            status_code=raw_response.status_code,
            headers=dict(raw_response.headers),
            elapsed_ms=raw_response.elapsed.total_seconds() * 1000,
            body=raw_response.text,
        )

        dict_response = response_as_dict(raw_response)

        # kalau mode debug -> return dict biar gampang inspect
        if self.settings.application.debug:
            return dict_response

        # kalau production mode -> return plain text clean
        return encode_response_upstream(dict_response)

    async def _execute(self, endpoint: str, params: dict) -> str | Dict[str, Any]:
        """Wrapper dengan error handling."""
        try:
            return await self._call_api_core(endpoint, params)
        except Exception as exc:
            self.log.error(f"Error executing {endpoint}: {exc}")
            raise exc

    async def get_balance(self) -> str | Dict[str, Any]:
        """Ambil saldo dari Digipos."""
        params = {"username": self.config.username}
        return await self._execute(self.config.endpoints.balance, params)

    async def get_profile(self) -> str | Dict[str, Any]:
        """Ambil profile Digipos."""
        params = {"username": self.config.username}
        return await self._execute(self.config.endpoints.profile, params)

    async def login(self) -> str | Dict[str, Any]:
        """Login ke Digipos."""
        params = {
            "username": self.config.username,
            "password": self.config.password,
        }
        return await self._execute(self.config.endpoints.login, params)
