import httpx
from httpx import AsyncClient
from loguru import logger

from src.config.cfg_api_clients import ApiBaseConfig
from src.core.client import ApiClientManager, HttpClientFactory


async def check_url_reachable(url: str, timeout: float = 1.0) -> bool:
    """Cek apakah base_url reachable tanpa ngeblok service."""
    log = logger.bind(service="URLValidator")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.head(url)
            reachable = response.status_code < 500
            log.debug(
                f"URL {url} reachable={reachable} (status={response.status_code})"
            )
            return reachable
    except Exception as exc:
        log.error(f"URL {url} tidak reachable: {exc}")
        return False


async def setup_client(
    manager: ApiClientManager, name: str, config: ApiBaseConfig, timeout: float = 1.0
) -> AsyncClient:
    if not await check_url_reachable(str(config.base_url), timeout=timeout):
        raise RuntimeError(f"Base URL '{config.base_url}' tidak reachable")

    client = HttpClientFactory.create_client(config)
    manager.register_client(name, client)
    return client
