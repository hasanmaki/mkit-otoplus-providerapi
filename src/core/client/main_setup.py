import httpx
from loguru import logger

from core.client.base_factory import HttpClientFactory
from core.client.base_manager import HttpClientManager
from src.core.config.cfg_api_clients import ApiBaseConfig


async def check_url_reachable(url: str, timeout: float | None = 1.0) -> bool:
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
        log.exception(f"URL {url} tidak reachable: {exc}")  # noqa: TRY401
        return False


async def setup_client(  # noqa: RUF029
    manager: HttpClientManager, config: ApiBaseConfig
) -> httpx.AsyncClient:
    """Setup client dari config dan register ke manager."""
    log = logger.bind(service=config.name)
    # if not await check_url_reachable(str(config.base_url)):
    #     raise RuntimeError(f"Base URL '{config.base_url}' tidak reachable")

    client = HttpClientFactory.create_client(config)
    manager.register_client(config.name, client)
    log.success(f"Client '{config.name}' initialized with base={config.base_url}")
    return client
