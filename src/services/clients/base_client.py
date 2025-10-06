# File: src/services/clients/base_client.py

from typing import Any

import httpx
from loguru import logger

from src.config.cfg_api_clients import ApiBaseConfig
from src.custom.exceptions import HTTPConnectionError, HttpResponseError


class BaseApiClient:
    """
    Base class untuk mengelola klien HTTP eksternal.
    Menyediakan fungsionalitas logging, error handling, dan response normalization.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        config: ApiBaseConfig,
    ):
        self.client = client
        self.config = config
        self.debug = config.debug
        self.log = logger.bind(
            client_name=self.__class__.__name__, base_url=config.base_url
        )

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        """Log request detail jika debug mode aktif."""
        if self.debug:
            headers = kwargs.get("headers", self.client.headers)
            self.log.debug(
                f"HTTP {method} {url} | headers={dict(headers)} | kwargs={kwargs}"
            )

    def _log_response(self, response: httpx.Response) -> None:
        """Log response detail jika debug mode aktif."""
        if self.debug:
            self.log.debug(
                f"Response [{response.status_code}] | headers={dict(response.headers)} | "
                f"body={response.text[:300]}"
            )

    def _handle_http_status_error(self, exc: httpx.HTTPStatusError) -> None:
        """Menangani 4xx/5xx status code dan raising HttpResponseError."""
        self.log.error(
            f"Response Error: {exc.response.status_code} | headers={dict(exc.response.headers)}"
        )
        raise HttpResponseError(
            message=f"External service responded with status {exc.response.status_code}",
            context={
                "url": str(exc.request.url),
                "request_headers": dict(exc.request.headers),
                "response_text": exc.response.text,
                "response_headers": dict(exc.response.headers),
            },
            cause=exc,
        ) from exc

    def _handle_request_error(self, exc: httpx.RequestError, url: str) -> None:
        """Menangani timeout, DNS error, atau koneksi gagal dan raising HTTPConnectionError."""
        self.log.error(f"Connection Error: {exc.__class__.__name__}")
        raise HTTPConnectionError(
            message=f"Connection error to external service: {exc.__class__.__name__}",
            context={
                "url": str(exc.request.url) if exc.request else url,
                "request_headers": dict(exc.request.headers) if exc.request else None,
            },
            cause=exc,
        ) from exc

    # --- CORE COMPOSER METHOD ---

    async def _handle_request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """Komposer utama: Log request, eksekusi, log response, dan handle error."""

        self._log_request(method, url, **kwargs)

        try:
            # 1. Eksekusi HTTP call
            response = await getattr(self.client, method.lower())(url, **kwargs)
            # 2. Periksa status code (akan raise HTTPStatusError jika 4xx/5xx)
            response.raise_for_status()

            # 3. Sukses
            self._log_response(response)
            return response

        # Tangani Request Errors (Timeout, Connection, DNS)
        except httpx.RequestError as exc:
            self._handle_request_error(exc, url)

        # Tangani Status Errors (4xx, 5xx)
        except httpx.HTTPStatusError as exc:
            self._handle_http_status_error(exc)

        raise Exception("Unhandled exception path reached.")

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Wrapper GET call."""
        return await self._handle_request("GET", url, **kwargs)
