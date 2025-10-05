"""Pendekatan sederhana dan friendly untuk mengatur AsyncClient."""

from typing import Dict

import httpx
from loguru import logger

from src.config.settings import get_settings


class ApiClientManager:
    def __init__(self):
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self.log = logger.bind(context="ApiClientManager")
        self.settings = get_settings()

    async def start(self):
        """Init semua HTTP client (reusable di seluruh app)."""
        self.log.info("Initializing HTTP clients...")

        digipos_cfg = self.settings.digipos
        self._clients["digipos"] = httpx.AsyncClient(
            base_url=str(digipos_cfg.base_url),
            headers=digipos_cfg.headers,
            timeout=digipos_cfg.timeout,
            http2=digipos_cfg.http2,
        )

        self.log.debug(f"Registered clients: {list(self._clients.keys())}")

    async def stop(self):
        """Close semua clients saat app shutdown."""
        self.log.info("Closing HTTP clients...")
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()

    def get_client(self, name: str) -> httpx.AsyncClient:
        """Ambil client berdasarkan nama provider."""
        if name not in self._clients:
            self.log.error(f"Client {name} belum diinisialisasi")
            raise ValueError(f"Client {name} belum diinisialisasi")
        return self._clients[name]
