import httpx

from src.config.cfg_api_clients import DigiposConfig
from src.core.clients.base import BaseClient
from src.custom.exceptions import AuthenticationError
from src.schemas.sch_digipos import RequestBalance, ResponseBalance


class DigiposApiClient(BaseClient):
    """Klien spesifik untuk Digipos API."""

    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig):
        super().__init__(client, config)
        self.config = config

    def validate_username(self, username: str) -> None:
        if username != self.config.username:
            raise AuthenticationError(
                message="Username provided does not match configured credentials.",
                context={"request_username": username},
            )

    async def get_balance(self, request_data: RequestBalance) -> ResponseBalance:
        self.validate_username(request_data.username)
        self.log.info(f"Mengecek saldo untuk user: {request_data.username}")
        resp = await self.cst_get(
            f"{self.config.base_url}balance", params=request_data.model_dump()
        )
        return ResponseBalance(**resp)
