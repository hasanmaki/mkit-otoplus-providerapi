"""bussines logic for digipos."""

from loguru import logger

from servicess.client.depre_cated_response_model import (
    ApiResponseIN,
    ApiResponseOUT,
)
from servicess.client.request import HttpRequestService
from servicess.digipos.sch_digipos import (
    DGReqSimStatus,
    DGReqUsername,
    DGReqUsnOtp,
    DGReqUsnPass,
    DGResBalance,
)
from servicess.parser.parser_utils import clean_validate_raw_dict_data
from src.core.config.cfg_api_clients import DigiposConfig
from src.servicess.digipos.auth_service import DigiposAuthService


class DGCommandServices:
    def __init__(
        self,
        http_service: HttpRequestService,
        auth_service: DigiposAuthService,
        setting: DigiposConfig,
    ):
        self.http_service = http_service
        self.auth_service = auth_service
        self.setting = setting
        self.logger = logger.bind(service="Digipos Command Service")

    async def login(self, data: DGReqUsnPass):
        """Ambil login dari Digipos API."""
        self.auth_service.validate_usnpass(data.username, data.password)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.login,
            params=data.model_dump(),
        )
        return raw_response

    async def verify_otp(self, data: DGReqUsnOtp):
        """Ambil verify OTP dari Digipos API."""
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.verify_otp,
            params=data.model_dump(),
        )
        return raw_response

    async def balance(self, data: DGReqUsername) -> ApiResponseOUT[DGResBalance]:
        """Ambil Balance dari Digipos API dan clean data."""
        self.auth_service.validate_username(data.username)

        # 1. Ambil raw response
        raw_response: ApiResponseIN = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.balance,
            params=data.model_dump(),
            debugresponse=data.debug,
        )
        final_response = clean_validate_raw_dict_data(raw_response, DGResBalance)
        return final_response

    async def profile(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.profile,
            params=data.model_dump(),
        )
        return raw_response

    async def list_va(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.list_va,
            params=data.model_dump(),
        )
        return raw_response

    async def reward(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.reward,
            params=data.model_dump(),
        )
        return raw_response

    async def banner(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.banner,
            params=data.model_dump(),
        )
        return raw_response

    async def logout(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.logout,
            params=data.model_dump(),
        )
        return raw_response

    # utils methode
    async def sim_status(self, data: DGReqSimStatus):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.sim_status,
            params=data.model_dump(),
        )
        return raw_response
