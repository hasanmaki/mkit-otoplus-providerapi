"""dsini hanya bertugas menentukan endpoint, dan internal bussines logic, masalah parse dan lain lain di lakukan di taempat lain."""

from src.config.settings import DigiposConfig
from src.core.client import HttpClientService
from src.schemas.sch_digipos import DGReqUsername, DGReqUsnOtp, DGReqUsnPass
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
        self.debug = setting.debug

    async def _short_call(self, endpoint: str, params: dict):
        return await self.http_service.safe_request(
            "GET", endpoint, params=params, debugresponse=self.debug
        )

    async def login(self, data: DGReqUsnPass):
        """Ambil login dari Digipos API."""
        self.auth_service.validate_usnpass(data.username, data.password)
        return await self._short_call(self.setting.endpoints.login, data.model_dump())

    async def verify_otp(self, data: DGReqUsnOtp):
        """Ambil verify OTP dari Digipos API."""
        self.auth_service.validate_username(data.username)
        return await self._short_call(
            self.setting.endpoints.verify_otp, data.model_dump()
        )

    async def balance(self, data: DGReqUsername):
        """Ambil Balance Dari Digipos API."""
        self.auth_service.validate_username(data.username)
        return await self._short_call(self.setting.endpoints.balance, data.model_dump())

    async def profile(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        return await self._short_call(self.setting.endpoints.profile, data.model_dump())

    async def list_va(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        return await self._short_call(self.setting.endpoints.list_va, data.model_dump())

    async def reward(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        return await self._short_call(self.setting.endpoints.reward, data.model_dump())

    async def banner(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        return await self._short_call(self.setting.endpoints.banner, data.model_dump())

    async def logout(self, data: DGReqUsername):
        self.auth_service.validate_username(data.username)
        return await self._short_call(self.setting.endpoints.logout, data.model_dump())
