from dataclasses import asdict, dataclass
from typing import Any

import httpx
from loguru import logger

from src.config.constant import ResponseMessage
from src.custom.exceptions import HTTPConnectionError, HttpResponseError


@dataclass
class NormalizedResponse:
    status_code: int
    url: str
    meta: dict[str, Any]
    message: str
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HttpServiceClient:
    def __init__(self, client: httpx.AsyncClient, service_name: str | None = None):
        inferred_name = service_name or getattr(client.base_url, "host", "Upstream")
        self.client = client
        self.log = logger.bind(service=inferred_name)

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        if method not in ["GET", "POST"]:
            raise ValueError(f"Invalid HTTP method: {method}")

        try:
            self.log.debug(f"issuing {method} request with endpoint: {endpoint}")
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

    def normalize(
        self, resp: httpx.Response, *, debug: bool = False
    ) -> NormalizedResponse:
        try:
            url = str(resp.request.url.copy_with(query=None))
            status = resp.status_code

            try:
                body = resp.json()
                if isinstance(body, dict):
                    data = body
                    msg = ResponseMessage.DICT
                elif isinstance(body, list):
                    data = {"items": body, "count": len(body)}
                    msg = ResponseMessage.LIST
                else:
                    data = {"raw": body}
                    msg = ResponseMessage.PRIMITIVE
            except Exception:
                text = resp.text.strip()
                data = {"raw": text or None}
                msg = ResponseMessage.TEXT if text else ResponseMessage.EMPTY_BODY

            meta = {}
            if debug:
                meta = {
                    "method": resp.request.method,
                    "headers": dict(resp.headers),
                    "elapsed": resp.elapsed.total_seconds(),
                }

            payload_type = type(data).__name__
            payload_size = len(str(data))
            content_type: str = resp.headers.get("content-type", "unknown")

            self.log.debug(
                f"{resp.request.method} {url} -> {status} | content_type={content_type} |type={payload_type}, size={payload_size}"
            )

            return NormalizedResponse(status, url, meta, msg, data)
        except Exception as exc:
            self.log.error(f"Normalize failed: {exc}")
            return NormalizedResponse(
                0, "unknown", {}, ResponseMessage.INTERNAL_ERROR, {"raw": str(exc)}
            )

    async def safe_request(self, method: str, endpoint: str, **kwargs) -> dict:
        try:
            resp = await self.request(method, endpoint, **kwargs)
            return self.normalize(resp).to_dict()
        except Exception as exc:
            self.log.error(f"Safe request failed: {exc}")
            return NormalizedResponse(
                0, endpoint, {}, ResponseMessage.INTERNAL_ERROR, {"error": str(exc)}
            ).to_dict()
