import httpx
from loguru import logger

from services.client.http_response import ResponseHandlerFactory
from src.custom.exceptions import (
    HTTPConnectionError,
    HttpResponseError,
    HTTPUnsupportedMethodeError,
)


class HttpRequestService:
    """HTTP client dengan auto parser berbasis content-type."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        response_handler: ResponseHandlerFactory,
        service_name: str | None = None,
    ):
        inferred_name = service_name or getattr(client.base_url, "host", "Upstream")
        self.client = client
        self.response_handler = response_handler
        self.log = logger.bind(service=inferred_name)

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Low level request (tanpa parsing)."""
        method = method.upper()

        if method not in {"GET"}:
            raise HTTPUnsupportedMethodeError(
                message="forbidden methode call",
                context={"method": method, "endpoint": endpoint},
            )
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
                    "body": exc.response.text[:500],
                },
                cause=exc,
            ) from exc
        return resp

    async def safe_request(
        self, method: str, endpoint: str, debugresponse: bool = False, **kwargs
    ):
        """High level call — otomatis parsing ke dict."""
        raw_response = await self._request(method, endpoint, **kwargs)
        return self.response_handler(raw_response, debugresponse)
