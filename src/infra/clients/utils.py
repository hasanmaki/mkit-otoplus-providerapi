import httpx
from loguru import logger


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
