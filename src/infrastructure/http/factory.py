from httpx import AsyncClient, Limits
from httpx_retries import Retry, RetryTransport
from loguru import logger
from src.config.client_config import ClientBaseConfig
from src.ports.http_client_factory import IHttpClientFactory


class HttpxClientFactory(IHttpClientFactory):
    """Httpx-specific factory implementation.

    SRP: Cuma fokus ke create & configure AsyncClient.
    """

    def __init__(self):
        self.log = logger.bind(factory="HttpxClientFactory")

    def create_client(self, config: ClientBaseConfig) -> AsyncClient:
        """Create fully configured AsyncClient.

        Handles:
        - Retry strategy
        - Connection pooling
        - Timeouts
        - HTTP/2 support
        """
        # 1. Setup retry strategy
        retry = self._create_retry_strategy(config)
        transport = RetryTransport(retry=retry)

        # 2. Setup connection limits
        limits = self._create_connection_limits(config)

        # 3. Log configuration
        self.log.debug(
            f"Creating client | name={config.name} | "
            f"base_url={config.base_url} | "
            f"max_conn={limits.max_connections} | "
            f"retry_total={retry.total}"
        )

        # 4. Build client
        client = AsyncClient(
            base_url=str(config.base_url),
            headers=config.headers,
            timeout=config.timeout,
            http2=config.http2,
            transport=transport,
            limits=limits,
        )

        self.log.success(f"Client '{config.name}' created successfully")
        return client

    def _create_retry_strategy(self, config: ClientBaseConfig) -> Retry:
        """Extract retry configuration."""
        return Retry(
            total=config.retry.total,
            backoff_factor=config.retry.backoff_factor,
            status_forcelist=config.retry.status_forcelist,
            allowed_methods=config.retry.allowed_methods,
        )

    def _create_connection_limits(self, config: ClientBaseConfig) -> Limits:
        """Extract connection limits configuration."""
        return Limits(
            max_keepalive_connections=config.limits.max_keepalive_connections,
            max_connections=config.limits.max_connections,
            keepalive_expiry=config.limits.keepalive_expiry,
        )
