from httpx import AsyncClient
from loguru import logger


class ApiClientManager:
    """Registry & lifecycle manager untuk semua AsyncClient."""

    def __init__(self) -> None:
        self._clients: dict[str, AsyncClient] = {}
        self.log = logger.bind(service="ApiClientManager")

    def register_client(self, name: str, client: AsyncClient) -> None:
        """Register 1 client siap pakai."""
        if name in self._clients:
            self.log.warning(f"Client '{name}' sudah terdaftar — dilewati.")
            return
        self._clients[name] = client
        self.log.debug(f"Client '{name}' registered successfully.")

    def get_client(self, name: str) -> AsyncClient:
        """Ambil client berdasarkan nama."""
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
