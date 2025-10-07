import httpx
from loguru import logger

from src.custom.exceptions import HTTPConnectionError, HttpResponseError


class HttpClientService:
    """HTTP client dengan auto parser berbasis content-type."""

    def __init__(self, client: httpx.AsyncClient, service_name: str | None = None):
        inferred_name = getattr(client.base_url, "host", "Upstream") or service_name
        self.client = client
        self.log = logger.bind(service=inferred_name)

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Low level request."""
        method = method.upper()
        if method not in ["GET", "POST"]:
            raise ValueError(f"Invalid HTTP method: {method}")
        try:
            self.log.debug(f"Issuing request: [{method}] to endpoint: [{endpoint}]")
            resp = await getattr(self.client, method.lower())(endpoint, **kwargs)
            resp.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPConnectionError(
                message="Connection error",
                context={"endpoint": endpoint, "details": str(exc)},
                cause=exc,
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise HttpResponseError(
                message=f"Bad status {exc.response.status_code}",
                context={"endpoint": endpoint, "text": exc.response.text},
                cause=exc,
            ) from exc
        return resp

    async def safe_request(
        self, method: str, endpoint: str, **kwargs
    ) -> httpx.Response:
        """Public Api wrapper."""
        raw_response = await self._request(method, endpoint, **kwargs)
        return raw_response
