# src/api_clients/digipos.py
import httpx

from src.config.cfg_api_clients import DigiposConfig
from src.core.clients.base import BaseClient
from src.custom.exceptions import AuthenticationError, HttpResponseError


class DigiposApiClient(BaseClient):
    """Klien spesifik untuk berinteraksi dengan Digipos API."""

    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig):
        super().__init__(client, config)
        self.config: DigiposConfig = config

    async def get_balance(self) -> dict:
        """Mengambil saldo dengan kredensial dari config."""
        payload = {
            "username": self.config.username,
        }

        # Menggunakan logger yang sudah terikat
        self.log.info(f"Mengecek saldo untuk user: {self.config.username}")

        try:
            response_data = await self.cst_get(url="/balance", params=payload)
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
