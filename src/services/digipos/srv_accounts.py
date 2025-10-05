"""services digipos related."""

from typing import Any, Dict, Type, Union

import httpx
from loguru import logger
from pydantic import ValidationError

from src.config.settings import DigiposConfig
from src.schemas.base_response import ApiResponse
from src.schemas.sch_digipos import ResponseBalance
from src.services.clients.base_client import BaseApiClient

# Asumsi path ini benar
from src.services.utils.output_utils import model_to_legacy_string
from src.services.utils.response_utils import response_upstream_to_dict


class ServiceDigiposAccount(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig) -> None:
        super().__init__(client, config)
        self.config: DigiposConfig = config
        # Mengambil tipe respons dari konfigurasi (misalnya 'json' atau 'text')
        self.response_type = config.response.type
        self.log_dgp = logger.bind(name="ServiceDigiposAccount")

    async def _call_api_core(self, endpoint: str, params: dict) -> Dict[str, Any]:
        """
        Fungsi inti: Menangani call API, logging, dan mengembalikan DICT
        yang dinormalisasi dari upstream.
        """
        raw_response = await self.cst_get(endpoint, params=params)

        self.log_dgp.debug(
            "Raw response captured",
            url=str(raw_response.request.url),
            method=raw_response.request.method,
            status_code=raw_response.status_code,
            headers=dict(raw_response.headers),
            elapsed_ms=raw_response.elapsed.total_seconds() * 1000,
            body=raw_response.text,
        )

        dict_response = response_upstream_to_dict(raw_response)
        return dict_response

    def _transform_response(
        self, dict_response: Dict[str, Any], response_model: Type[Any]
    ) -> Union[Any, str]:
        """Melakukan validasi Pydantic yang aman dan transformasi output berdasarkan config."""

        # A. VALIDASI PYDANTIC (INTERNAL)
        try:
            # Coba validasi ke model spesifik (ResponseBalance, ApiResponse, dll.)
            pydantic_model = response_model(**dict_response)
        except ValidationError as e:
            # Jika gagal, fallback ke ApiResponse generik untuk struktur yang aman
            self.log_dgp.error(
                "Pydantic Validation failed, falling back to generic model.",
                error=str(e),
                data=dict_response,
            )
            # Pastikan selalu menggunakan ApiResponse generik sebagai fallback
            pydantic_model = ApiResponse(**dict_response)

        # B. SERIALISASI OUTPUT (EXTERNAL)
        if self.response_type == "text":
            # Jika klien mengharapkan format legacy (string flattened)
            return model_to_legacy_string(pydantic_model)
        else:
            # Jika klien mengharapkan JSON (default), kembalikan Pydantic Model
            return pydantic_model

    # ----------------------------------------------------------------------
    #                          SERVICE METHODS (TRANSFORMED)
    # ----------------------------------------------------------------------

    async def get_login(self) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.login,
            {"username": self.config.username, "password": self.config.password},
        )
        return self._transform_response(dict_response, ApiResponse)

    async def get_verify_otp(self, otp: str) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.verify_otp,
            {"username": self.config.username, "otp": otp},
        )
        return self._transform_response(dict_response, ApiResponse)

    async def get_balance(self) -> Union[ResponseBalance, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.balance,
            {"username": self.config.username},
        )
        return self._transform_response(dict_response, ResponseBalance)

    async def get_profile(self) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.profile,
            {"username": self.config.username},
        )
        return self._transform_response(dict_response, ApiResponse)

    async def get_list_va(self) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.list_va,
            {"username": self.config.username},
        )
        return self._transform_response(dict_response, ApiResponse)

    async def get_rewardsummary(self) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.reward,
            {"username": self.config.username},
        )
        return self._transform_response(dict_response, ApiResponse)

    async def get_banner(self) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.banner,
            {"username": self.config.username},
        )
        return self._transform_response(dict_response, ApiResponse)

    async def get_logout(self) -> Union[ApiResponse, str]:
        dict_response = await self._call_api_core(
            self.config.endpoints.logout,
            {"username": self.config.username},
        )
        return self._transform_response(dict_response, ApiResponse)
