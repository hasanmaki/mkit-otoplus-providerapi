import httpx
from httpx import AsyncClient
from loguru import logger
from src.config.client_config import ClientBaseConfig

from infra.clients.factory import HttpClientFactory
from infra.clients.utils import check_url_reachable


class HttpClientManager:
    """Registry & lifecycle manager untuk semua AsyncClient."""

    def __init__(self, factory: HttpClientFactory) -> None:
        # Inisialisasi dengan Factory untuk DECOUPLING (injeksi)
        self._clients: dict[str, AsyncClient] = {}
        self._factory = factory
        self.log = logger.bind(service="HttpClientManager")

    def _register_client(self, name: str, client: AsyncClient) -> None:
        if name in self._clients:
            self.log.warning(f"Client '{name}' sudah terdaftar — dilewati.")
            return
        self._clients[name] = client
        self.log.debug(f"Client '{name}' registered successfully.")

    async def setup_and_register_client(
        self, config: ClientBaseConfig, check_url: bool = False
    ) -> httpx.AsyncClient:
        """Setup client dari config, melakukan check, dan register ke manager."""
        log = self.log.bind(client_name=config.name)
        if check_url and not await check_url_reachable(str(config.base_url)):
            log.error(f"Base URL '{config.base_url}' tidak reachable")
            raise RuntimeError(f"Base URL '{config.base_url}' tidak reachable")

        # 2. Create client menggunakan Factory yang diinjeksikan
        client = self._factory.create_client(config)

        # 3. Register
        self._register_client(config.name, client)

        log.success(f"Client '{config.name}' initialized with base={config.base_url}")
        return client

    def get_client(self, name: str) -> AsyncClient:
        if name not in self._clients:
            self.log.error(f"Client '{name}' belum diinisialisasi")
            raise ValueError(f"Client '{name}' belum diinisialisasi")
        return self._clients[name]

    async def start_all(self):
        """Opsional: start tasks per client, jika perlu."""
        self.log.info("Starting all registered clients...")
        self.log.success(f"Clients started: {list(self._clients.keys())}")

    async def stop_all(self):
        """Tutup semua koneksi dan clear registry."""
        self.log.info("Closing all clients...")
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()
        self.log.success("All HTTP clients closed successfully.")
