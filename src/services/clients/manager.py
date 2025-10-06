from typing import Dict

import httpx
from httpx_retries import Retry, RetryTransport
from loguru import logger

from src.config import settings
from src.config.settings import get_settings


class ApiClientManager:
    """
    Centralized manager untuk semua Async HTTP Client (reusable & global).
    - Handle retry, limit, keepalive, dan lifecycle client
    """

    def __init__(self) -> None:
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self.log = logger.bind(context="ApiClientManager")
        self.settings = get_settings()

    async def start(self) -> None:
        """Inisialisasi semua client global di startup."""
        self.log.info("Initializing HTTP clients...")

        # --- build retry strategy ---
        client_settings: settings.ClientBaseConfig = settings.AppSettings.client
        retry = Retry(
            total=client_settings.retry.total,
            backoff_factor=client_settings.retry.backoff_factor,  # exponential delay
            status_forcelist=client_settings.retry.status_forcelist,
            allowed_methods=client_settings.retry.allowed_methods,
        )

        transport = RetryTransport(retry=retry)

        # --- build connection limits ---

        limits = httpx.Limits(
            max_keepalive_connections=client_settings.limits.max_keepalive_connections,
            max_connections=client_settings.limits.max_connections,
            keepalive_expiry=client_settings.limits.keepalive_expiry,  # 5 menit
        )

        # --- register digipos client (default) ---
        digipos_cfg = self.settings.digipos

        await self.register_client(
            name="digipos",
            base_url=str(digipos_cfg.base_url),
            headers=digipos_cfg.headers,
            timeout=digipos_cfg.timeout,
            http2=digipos_cfg.http2,
            transport=transport,
            limits=limits,
        )

        self.log.success(f"Registered clients: {list(self._clients.keys())}")

    async def register_client(
        self,
        name: str,
        base_url: str,
        headers: dict,
        timeout: float | int,
        http2: bool = False,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        limits: httpx.Limits | None = None,
    ) -> None:
        """Register 1 client baru dengan konfigurasi lengkap."""
        if name in self._clients:
            self.log.warning(f"Client '{name}' sudah terdaftar — dilewati.")
            return

        client = httpx.AsyncClient(
            transport=transport,
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            http2=http2,
            limits=limits,  # type: ignore
        )

        self._clients[name] = client
        self.log.debug(
            f"HTTP client '{name}' initialized | "
            f"base_url={base_url} | retry={getattr(transport, 'retry', None)} | "
            f"max_conn={limits.max_connections if limits else 'default'}"
        )

    async def stop(self) -> None:
        """Tutup semua koneksi saat app shutdown."""
        self.log.info("Closing HTTP clients...")
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()
        self.log.success("All HTTP clients closed successfully.")

    def get_client(self, name: str) -> httpx.AsyncClient:
        """Ambil client berdasarkan nama provider."""
        if name not in self._clients:
            self.log.error(f"Client '{name}' belum diinisialisasi")
            raise ValueError(f"Client '{name}' belum diinisialisasi")
        return self._clients[name]
