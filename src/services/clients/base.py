from typing import Any, Dict

import httpx
from loguru import logger

from src.config.cfg_api_clients import ApiBaseConfig
from src.custom.exceptions import HTTPConnectionError, HttpResponseError


class BaseApiClient:
    """Base class untuk mengelola klien HTTP eksternal."""

    def __init__(self, client: httpx.AsyncClient, config: ApiBaseConfig):
        self.client = client
        self.config = config
        self.log = logger.bind(
            client_name=self.__class__.__name__, base_url=config.base_url
        )

    async def _handle_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        self.log.debug(f"HTTP {method} {url} {kwargs}")
        try:
            response = await getattr(self.client, method.lower())(url, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self.log.error(
                f"Response Error: {exc.response.status_code}",
                status=exc.response.status_code,
            )
            raise HttpResponseError(
                message=f"External service responded with status {exc.response.status_code}",
                context={
                    "url": str(exc.request.url),
                    "response_text": exc.response.text,
                },
                cause=exc,
            ) from exc

        except httpx.RequestError as exc:
            self.log.error(
                f"Connection Error: {exc.__class__.__name__}", url=str(exc.request.url)
            )
            raise HTTPConnectionError(
                message=f"Connection error to external service: {exc.__class__.__name__}",
                context={"url": str(exc.request.url) if exc.request else url},
                cause=exc,
            ) from exc
        return response.json()

    async def cst_get(self, url: str, **kwargs) -> Dict[str, Any]:
        return await self._handle_request("GET", url, **kwargs)
