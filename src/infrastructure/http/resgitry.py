from httpx import AsyncClient
from loguru import logger
from src.custom.exceptions import (
    ClientAlreadyRegisteredError,
    ClientNotFoundError,
)
from src.ports.http_client_factory import IHttpClientRegistry


class HttpClientRegistry(IHttpClientRegistry):
    """In-memory registry untuk manage HTTP clients.

    SRP: Cuma handle storage & retrieval, NO business logic.
    """

    def __init__(self):
        self._clients: dict[str, AsyncClient] = {}
        self.log = logger.bind(registry="HttpClientRegistry")

    def register(self, name: str, client: AsyncClient) -> None:
        """Register client dengan validation.

        Raises:
            ClientAlreadyRegisteredError: If client already exists
        """
        if name in self._clients:
            self.log.warning(f"Client '{name}' already registered")
            raise ClientAlreadyRegisteredError(name)

        self._clients[name] = client
        self.log.debug(f"Client '{name}' registered | total={len(self._clients)}")

    def get(self, name: str) -> AsyncClient:
        """Get registered client.

        Raises:
            ClientNotFoundError: If client not found
        """
        if name not in self._clients:
            self.log.error(f"Client '{name}' not found")
            raise ClientNotFoundError(name)

        return self._clients[name]

    def has(self, name: str) -> bool:
        """Check if client exists."""
        return name in self._clients

    def list_clients(self) -> list[str]:
        """Get all registered client names."""
        return list(self._clients.keys())

    async def close_all(self) -> None:
        """Close all clients and clear registry."""
        self.log.info(f"Closing {len(self._clients)} clients...")

        for name, client in self._clients.items():
            try:
                await client.aclose()
                self.log.debug(f"Client '{name}' closed")
            except Exception as e:
                self.log.error(f"Error closing client '{name}': {e}")  # noqa: TRY400

        self._clients.clear()
        self.log.success("All clients closed successfully")
