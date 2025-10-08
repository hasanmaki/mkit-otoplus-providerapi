import httpx
from loguru import logger

from services.client.http_response import ResponseParserFactory
from src.custom.exceptions import HTTPConnectionError, HttpResponseError


class HttpRequestService:
    """HTTP client dengan auto parser berbasis content-type."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        parser_factory: ResponseParserFactory,
        service_name: str | None = None,
    ):
        # fallback name untuk log clarity
        inferred_name = service_name or getattr(client.base_url, "host", "Upstream")
        self.client = client
        self.parser_factory = parser_factory
        self.log = logger.bind(service=inferred_name)

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Low level request (tanpa parsing)."""
        method = method.upper()

        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError(f"Invalid HTTP method: {method}")

        try:
            self.log.debug(f"Request [{method}] -> {endpoint}")
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
                message=f"Bad status: {exc.response.status_code}",
                context={
                    "endpoint": endpoint,
                    "status_code": exc.response.status_code,
                    "body": exc.response.text[:500],  # limit biar log gak flood
                },
                cause=exc,
            ) from exc
        return resp

    async def safe_request(
        self, method: str, endpoint: str, debugresponse: bool = False, **kwargs
    ):
        """High level call — otomatis parsing ke dict."""
        raw_response = await self._request(method, endpoint, **kwargs)
        return self.parser_factory(raw_response, debugresponse)
