from httpx import AsyncClient, Limits
from httpx_retries import Retry, RetryTransport
from loguru import logger
from src.config.client_config import ClientBaseConfig


class HttpClientFactory:
    """Factory untuk membuat AsyncClient siap pakai dari config."""

    @staticmethod
    def create_client(config: ClientBaseConfig) -> AsyncClient:
        log = logger.bind(service="HttpClientFactory")

        # Setup retry strategy
        retry = Retry(
            total=config.retry.total,
            backoff_factor=config.retry.backoff_factor,
            status_forcelist=config.retry.status_forcelist,
            allowed_methods=config.retry.allowed_methods,
        )
        transport = RetryTransport(retry=retry)

        # Setup connection limits
        limits = Limits(
            max_keepalive_connections=config.limits.max_keepalive_connections,
            max_connections=config.limits.max_connections,
            keepalive_expiry=config.limits.keepalive_expiry,
        )

        log.debug(
            f"Creating AsyncClient | base_url={config.base_url} | "
            f"max_conn={limits.max_connections} | retry_total={retry.total}"
        )

        client = AsyncClient(
            base_url=str(config.base_url),
            headers=config.headers,
            timeout=config.timeout,
            http2=config.http2,
            transport=transport,
            limits=limits,
        )
        return client
