"""bussines logic for digipos."""

from loguru import logger
from pydantic import BaseModel, ValidationError

from services.client.http_request import HttpRequestService
from services.client.response_model import (
    ApiResponseIN,
    ApiResponseOUT,
    CleanAndParseStatus,
)
from services.digipos.sch_digipos import (
    DGReqSimStatus,
    DGReqUsername,
    DGReqUsnOtp,
    DGReqUsnPass,
)
from src.config.settings import DigiposConfig
from src.services.digipos.auth_service import DigiposAuthService


class BalanceData(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


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

    async def balance(self, data: DGReqUsername) -> ApiResponseOUT[BalanceData]:
        """Ambil Balance dari Digipos API dan clean data."""
        self.auth_service.validate_username(data.username)

        # 1. Ambil raw response
        raw_response: ApiResponseIN = await self.http_service.safe_request(
            method="GET",
            endpoint=self.setting.endpoints.balance,
            params=data.model_dump(),
            debugresponse=data.debug,
        )

        # 2. Parse/clean data
        try:
            clean_data = BalanceData.model_validate(raw_response.raw_data)
            parse_status = CleanAndParseStatus.SUCCESS
            description = "Data berhasil di-parse"
        except ValidationError as e:
            clean_data = raw_response.raw_data  # fallback: raw
            parse_status = CleanAndParseStatus.ERROR
            description = f"Error cleansing data: {e}"

        # 3. Bangun output standar
        return ApiResponseOUT[BalanceData](
            status_code=raw_response.status_code,
            url=raw_response.url,
            debug=raw_response.debug,
            meta=raw_response.meta,
            parse=parse_status,
            cleaned_data=clean_data,
            description=description,
        )

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
