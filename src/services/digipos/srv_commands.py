# File: src/services/digipos/commands.py (Koreksi)

from httpx import AsyncClient
from loguru import logger

from src.config.settings import DigiposConfig
from src.services.clients.request_utils import safe_fetch
from src.services.digipos.srv_reponse import DigiposResponse


class DigiposCommands:
    """Class Murni: Bertanggung jawab MENGAMBIL data mentah dari API."""

    def __init__(self, config: DigiposConfig):
        self.config = config
        self.log = logger.bind(service="digipos_commands")

    async def get_balance(self, client: AsyncClient) -> DigiposResponse:
        params = {"username": self.config.username}
        url: str = str(self.config.base_url) + self.config.endpoints.balance
        http_response = await safe_fetch(
            client=client,
            method="GET",
            url=url,
            log_context="digipos_balance",
            params=params,
        )
        return DigiposResponse(http_response)
