# src/infrastructure/clients/base_adapter.py (Refactored)

from abc import ABC, abstractmethod

import httpx
from loguru import logger
from src.custom.exceptions import (
    HTTPConnectionError,
    HttpResponseError,
)


class BaseHttpxAdapter(ABC):
    def __init__(self, client: httpx.AsyncClient, service_name: str | None = None):
        self.client = client
        inferred_name = service_name or getattr(client.base_url, "host", "Upstream")
        self.log = logger.bind(service=inferred_name)

    @abstractmethod
    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Abstract method for making HTTP requests."""
        raise NotImplementedError

    async def _base_request(
        self, method: str, endpoint: str, **kwargs
    ) -> httpx.Response:
        """Low level request, menangani I/O dan exception teknis."""
        method = method.upper()

        try:
            self.log.debug(f"Request [{method}] -> {endpoint}")
            raw_response = await getattr(self.client, method.lower())(
                endpoint, **kwargs
            )
            raw_response.raise_for_status()

        except httpx.RequestError as exc:
            # 💡 Menerjemahkan I/O Error
            raise HTTPConnectionError(
                message="Connection error",
                context={"endpoint": endpoint, "details": str(exc)},
                cause=exc,
            ) from exc

        except httpx.HTTPStatusError as exc:
            # 💡 Menerjemahkan HTTP Error
            # Adapter spesifik (Digipos/iSimple) akan menangkap ini dan menerjemahkan ke Domain Error
            raise HttpResponseError(
                message=f"Bad status: {exc.response.status_code}",
                context={"endpoint": endpoint, "status_code": exc.response.status_code},
                cause=exc,
            ) from exc
        return raw_response
