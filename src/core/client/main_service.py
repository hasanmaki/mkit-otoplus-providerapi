from typing import Any

import httpx
from loguru import logger

from core.client.base_parser import parse_response
from core.client.base_response_model import NormalizedResponse
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

    def _normalize(
        self, resp: httpx.Response, *, debug: bool = False
    ) -> NormalizedResponse:
        """Normalize the response from raw response http."""
        try:
            msg, data = parse_response(resp)

            meta = {}
            if debug:
                meta = {
                    "method": resp.request.method,
                    "headers": dict(resp.headers),
                    "elapsed": getattr(resp.elapsed, "total_seconds", lambda: None)(),
                    "http_version": getattr(resp, "http_version", "unknown"),
                }

            return NormalizedResponse.ok(resp, message=msg, data=data, meta=meta)
        except Exception as exc:
            self.log.error(f"Normalize failed: {exc}")  # noqa: TRY400
            return NormalizedResponse.error(str(resp.request.url), error=exc)

    async def safe_request(
        self, method: str, endpoint: str, debugresponse: bool = False, **kwargs
    ) -> dict[str, Any]:
        """Public Api wrapper."""
        try:
            resp = await self._request(method, endpoint, **kwargs)
            if debugresponse:
                response_preview = resp.text[:1000]
                self.log.debug(f"Response preview: {response_preview}")
            normalized: NormalizedResponse = self._normalize(resp, debug=debugresponse)
            return normalized.to_dict()
        except Exception as exc:
            self.log.error(f"Safe request failed: {exc}")  # noqa: TRY400
            return NormalizedResponse.error(endpoint, error=exc).to_dict()
