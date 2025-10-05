"""digipos account service related."""

from core.service_request import CoreApiRequestService
from core.service_response import context_to_dict
from src.domain.digipos.schemas import (
    DGReqLogin,
    DgVerifyOtp,
    DGWithUserName,
)


def _remove_nulls(d):
    if isinstance(d, dict):
        return {k: _remove_nulls(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [_remove_nulls(i) for i in d]
    else:
        return d


class DGAccountServices(CoreApiRequestService):
    """Digipos account related service class."""

    async def login(self, request: DGReqLogin) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send("GET", self.settings.endpoints.login, payload)
        normalized_response = context_to_dict(self.settings, raw_response)
        return normalized_response

    async def logout(self, request: DGWithUserName) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send("GET", self.settings.endpoints.logout, payload)
        normalized_response = context_to_dict(self.settings, raw_response)
        return normalized_response

    async def verify_otp(self, request: DgVerifyOtp) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send(
            "GET", self.settings.endpoints.verify_otp, payload
        )
        normalized_response = context_to_dict(self.settings, raw_response)
        return normalized_response

    async def balance(self, request: DGWithUserName) -> dict:
        payload = request.model_dump(
            exclude_none=True,
        )
        raw_response = await self._send("GET", self.settings.endpoints.balance, payload)
        normalized_response = context_to_dict(self.settings, raw_response)

        return normalized_response

    async def profile(self, request: DGWithUserName) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send("GET", self.settings.endpoints.profile, payload)
        normalized_response = context_to_dict(self.settings, raw_response)
        # replace only the 'data' field with outlet and user
        if "data" in normalized_response:
            inner_data = normalized_response["data"].get("data", {})
            outlet_data = inner_data.get("outlet", {})
            user_data = inner_data.get("user", {})

            # remove null values from both dicts

            outlet_data_clean = _remove_nulls(outlet_data)
            user_data_clean = _remove_nulls(user_data)
            normalized_response["data"]["data"] = {
                "outlet": outlet_data_clean,
                "user": user_data_clean,
            }
        return normalized_response

    async def list_va(self, request: DGWithUserName) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send("GET", self.settings.endpoints.list_va, payload)
        normalized_response = context_to_dict(self.settings, raw_response)

        if "data" in normalized_response and "data" in normalized_response["data"]:
            inner_data = normalized_response["data"]["data"]
            linkaja_data = inner_data.get("linkaja")
            finpay_data = inner_data.get("finpay")

            # assign only if not None
            if linkaja_data is not None:
                normalized_response["data"]["linkaja"] = _remove_nulls(linkaja_data)
            if finpay_data is not None:
                normalized_response["data"]["finpay"] = _remove_nulls(finpay_data)
            # remove 'data' key inside 'data' if exists
            del normalized_response["data"]["data"]
        return normalized_response

    async def reward_summary(self, request: DGWithUserName) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send(
            "GET", self.settings.endpoints.reward_summary, payload
        )
        return raw_response.json()

    async def banner(self, request: DGWithUserName) -> dict:
        payload = request.model_dump(exclude_none=True)
        raw_response = await self._send("GET", self.settings.endpoints.banner, payload)
        return raw_response.json()
