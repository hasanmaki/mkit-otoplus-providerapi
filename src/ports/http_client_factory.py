from typing import Protocol

from httpx import AsyncClient
from src.config.client_config import ClientBaseConfig


class IHttpClientFactory(Protocol):
    """Contract untuk factory yang create AsyncClient.

    Ini bikin kita bisa swap implementation (e.g., mock for testing).
    """

    def create_client(self, config: ClientBaseConfig) -> AsyncClient:
        """Create configured AsyncClient from config.

        Args:
            config: Client configuration

        Returns:
            Configured AsyncClient instance
        """
        ...


class IHttpClientRegistry(Protocol):
    """Contract untuk client registry/manager."""

    def register(self, name: str, client: AsyncClient) -> None:
        """Register a client with given name."""
        ...

    def get(self, name: str) -> AsyncClient:
        """Get registered client by name."""
        ...

    def has(self, name: str) -> bool:
        """Check if client is registered."""
        ...

    def list_clients(self) -> list[str]:
        """Get list of registered client names."""
        ...

    async def close_all(self) -> None:
        """Close all registered clients."""
        ...
