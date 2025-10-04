"""pendekatan lebih sederahan dan friendly untuk mengatur asyncclient."""

from typing import Dict

import httpx

from src.config.settings import get_settings

digipos_api_settings = get_settings().digipos
# isimp_api_settings = get_settings().isimple


class ApiClientManager:
    def __init__(self):
        self._clients: Dict[str, httpx.AsyncClient] = {}

    async def start(self):
        """Init all API clients (reusable across requests)."""
        print("Starting HTTP clients...")
        self._clients["digipos"] = httpx.AsyncClient(
            base_url=digipos_api_settings.base_url,
            headers=digipos_api_settings.headers,
            timeout=digipos_api_settings.timeout,
            http2=digipos_api_settings.http2,
        )
        self._clients["isat"] = httpx.AsyncClient(
            base_url="https://api.indosat.id", timeout=10
        )

    async def stop(self):
        """Close all clients when app shuts down."""
        print("Closing HTTP clients...")
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()

    def get(self, name: str) -> httpx.AsyncClient:
        """Return an existing client by provider name."""
        if name not in self._clients:
            raise ValueError(f"Client {name} belum diinisialisasi")
        return self._clients[name]


# singleton
client_manager = ApiClientManager()


def get_manager() -> ApiClientManager:
    return client_manager
