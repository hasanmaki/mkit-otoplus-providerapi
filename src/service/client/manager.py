from httpx import AsyncClient
from loguru import logger
from src.config.client_config import ClientBaseConfig
from src.custom.exceptions import ClientAlreadyRegisteredError
from src.ports.http_client_factory import IHttpClientFactory, IHttpClientRegistry


class HttpClientManager:
    """High-level orchestrator untuk client lifecycle.

    Responsibilities:
    - Setup clients from config
    - Coordinate factory & registry
    - Handle initialization errors
    - Manage lifecycle (startup/shutdown)

    TIDAK melakukan low-level operations (delegated ke registry & factory).
    """

    def __init__(
        self,
        factory: IHttpClientFactory,  # ✅ Depend on abstraction!
        registry: IHttpClientRegistry,  # ✅ Depend on abstraction!
    ):
        self._factory = factory
        self._registry = registry
        self.log = logger.bind(service="HttpClientManager")

    async def setup_client(self, config: ClientBaseConfig) -> AsyncClient:
        """Setup & register client dari config.

        Returns:
            Configured AsyncClient

        Raises:
            ClientAlreadyRegisteredError: If client already registered
        """
        log = self.log.bind(client_name=config.name)

        try:
            log.debug(f"Setting up client '{config.name}'...")
            client = self._factory.create_client(config)
            self._registry.register(config.name, client)
        except ClientAlreadyRegisteredError:
            log.warning(f"Client '{config.name}' already exists, returning existing")
            return self._registry.get(config.name)

        except Exception as e:
            log.error(f"Failed to setup client '{config.name}': {e}")  # noqa: TRY400
            raise
        log.success(f"Client '{config.name}' ready | base_url={config.base_url}")
        return client

    async def setup_clients(self, configs: list[ClientBaseConfig]) -> None:
        """Setup multiple clients dari list of configs.

        Useful untuk batch initialization di startup.
        """
        self.log.info(f"Setting up {len(configs)} clients...")

        for config in configs:
            try:
                await self.setup_client(config)
            except Exception as e:
                self.log.error(f"Failed to setup '{config.name}': {e}")  # noqa: TRY400
                # Continue dengan clients lainnya

        self.log.success(
            f"Setup complete | registered={len(self._registry.list_clients())}"
        )

    def get_client(self, name: str) -> AsyncClient:
        """Get registered client by name.

        Raises:
            ClientNotFoundError: If client not found
        """
        return self._registry.get(name)

    def has_client(self, name: str) -> bool:
        """Check if client is registered."""
        return self._registry.has(name)

    def list_clients(self) -> list[str]:
        """Get all registered client names."""
        return self._registry.list_clients()

    async def startup(self) -> None:
        """Lifecycle hook: Called saat application startup.

        Override ini untuk custom startup logic (e.g., health checks).
        """
        clients = self._registry.list_clients()
        self.log.info(f"HttpClientManager started | clients={clients}")

    async def shutdown(self) -> None:
        """Lifecycle hook: Called saat application shutdown.

        Ensures all clients properly closed.
        """
        self.log.info("Shutting down HttpClientManager...")
        await self._registry.close_all()
        self.log.success("HttpClientManager shutdown complete")
