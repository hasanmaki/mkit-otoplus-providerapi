"""bussines logic for digipos."""

from loguru import logger

from core.client.service_parser import response_to_dict
from core.client.service_request import HttpClientService
from src.config.settings import DigiposConfig
from src.schemas.sch_digipos import (
    DGReqSimStatus,
    DGReqUsername,
    DGReqUsnOtp,
    DGReqUsnPass,
)
from src.services.digipos.auth_service import DigiposAuthService


class DGCommandServices:
    def __init__(
        self,
        http_service: HttpClientService,
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
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)

        return dict_response

    async def verify_otp(self, data: DGReqUsnOtp):
        """Ambil verify OTP dari Digipos API."""
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.verify_otp,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)

        return dict_response

    async def balance(self, data: DGReqUsername):
        """Ambil Balance Dari Digipos API."""
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.balance,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)

        return dict_response

    async def profile(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.profile,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)
        return dict_response

    async def list_va(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.list_va,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)
        return dict_response

    async def reward(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.reward,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)
        return dict_response

    async def banner(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.banner,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)
        return dict_response

    async def logout(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.logout,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)
        return dict_response

    # utils methode
    async def sim_status(self, data: DGReqSimStatus):
        self.auth_service.validate_username(data.username)
        raw_response = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.sim_status,
            params=data.model_dump(),
        )
        dict_response = response_to_dict(raw_response, debugresponse=data.debug)
        return dict_response
