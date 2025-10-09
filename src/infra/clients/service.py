import httpx
from loguru import logger

from src.custom.exceptions import HTTPConnectionError, HttpResponseError


class HttpxClientService:
    """Low-level HTTP service (pure infra)."""

    def __init__(self, client: httpx.AsyncClient, service_name: str | None = None):
        self.client = client
        inferred_name = service_name or getattr(client.base_url, "host", "Upstream")
        self.log = logger.bind(service=inferred_name)

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        method = method.upper()
        try:
            self.log.debug(f"Request [{method}] -> {endpoint}")
            raw_response = await getattr(self.client, method.lower())(
                endpoint, **kwargs
            )
            raw_response.raise_for_status()

        except httpx.RequestError as exc:
            self.log.error(f"Connection problem -> {exc}")  # noqa: TRY400
            raise HTTPConnectionError(
                message="Connection error",
                context={"endpoint": endpoint, "details": str(exc)},
                cause=exc,
            ) from exc
        except httpx.HTTPStatusError as exc:
            self.log.error(f"HTTP status problem -> {exc}")  # noqa: TRY400
            raise HttpResponseError(
                message=f"Bad status: {exc.response.status_code}",
                context={"endpoint": endpoint, "status_code": exc.response.status_code},
                cause=exc,
            ) from exc
        return raw_response
