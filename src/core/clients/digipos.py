# src/api_clients/digipos.py
import httpx

from src.config.cfg_api_clients import DigiposConfig
from src.core.clients.base import BaseClient
from src.custom.exceptions import AuthenticationError, HttpResponseError
from src.schemas.sch_digipos import RequestBalance


class DigiposApiClient(BaseClient):
    """Klien spesifik untuk berinteraksi dengan Digipos API."""

    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig):
        super().__init__(client, config)
        self.config: DigiposConfig = config

    async def get_balance(self, request_data: RequestBalance) -> dict:
        if request_data.username != self.config.username:
            self.log.warning(
                f"Username mismatch: Request='{request_data.username}' Config='{self.config.username}'"
            )
            raise AuthenticationError(
                message="Username provided does not match configured credentials.",
                context={"request_username": request_data.username},
            )

        payload = {
            "username": request_data.username,
        }

        # Menggunakan logger yang sudah terikat
        self.log.info(f"Mengecek saldo untuk user: {request_data.username}")

        try:
            _status_code, response_data = await self.cst_get(url="/balance", params=payload)
            return response_data
        except HttpResponseError as exc:
            # Contoh penanganan error spesifik dari Digipos
            if "INVALID_CREDENTIALS" in exc.context.get("response_text", ""):
                raise AuthenticationError(
                    message="Digipos authentication failed.",
                    context={"user": self.config.username},
                    cause=exc,
                ) from exc
            raise
