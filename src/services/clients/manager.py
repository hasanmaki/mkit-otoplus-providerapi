"""pendekatan lebih sederahan dan friendly untuk mengatur asyncclient."""

from typing import Dict

import httpx
from loguru import logger

from src.config.settings import get_settings

digipos_api_settings = get_settings().digipos


class ApiClientManager:
    def __init__(self):
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self.apilog = logger.bind(name="ApiClientManager")

    async def start(self):
        """Init all API clients (reusable across requests)."""
        self.apilog.info("Initializing HTTP clients...")
        self._clients["digipos"] = httpx.AsyncClient(
            base_url=str(digipos_api_settings.base_url),
            headers=digipos_api_settings.headers,
            timeout=digipos_api_settings.timeout,
            http2=digipos_api_settings.http2,
        )
        self.apilog.debug(f"getting clints id {self._clients}")

    async def stop(self):
        """Close all clients when app shuts down."""
        self.apilog.info("Closing HTTP clients...")
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()

    def get_client(self, name: str) -> httpx.AsyncClient:
        """Return an existing client by provider name."""
        if name not in self._clients:
            self.apilog.error(f"Client {name} belum diinisialisasi")
            raise ValueError(f"Client {name} belum diinisialisasi")
        self.apilog.debug(f"getting clints id {self._clients}")
        return self._clients[name]
