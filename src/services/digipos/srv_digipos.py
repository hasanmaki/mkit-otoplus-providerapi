"""services digipos related."""

import httpx

from src.config.settings import DigiposConfig
from src.services.clients.base import BaseApiClient


class ServiceDigipos(BaseApiClient):
    def __init__(self, client: httpx.AsyncClient, config: DigiposConfig) -> None:
        super().__init__(client, config)
        self.config: DigiposConfig = config
        self.response_type = config.response.type

    async def get_balance(self):
        """get balance from digipos."""
        endpoint = self.config.endpoints.balance
        params = {"username": self.config.username}
        response = await self.cst_get(endpoint, params=params)
        return response
