from typing import Any, Dict

import httpx
from loguru import logger

from src.config.cfg_api_clients import ApiBaseConfig
from src.custom.exceptions import HTTPConnectionError, HttpResponseError
from src.services.utils.response_utils import response_to_normalized_dict


class BaseApiClient:
    """Base class untuk mengelola klien HTTP eksternal."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        config: ApiBaseConfig,
    ):
        self.client = client
        self.config = config
        # Mengambil debug flag langsung dari config klien
        self.debug = config.debug
        self.log = logger.bind(
            client_name=self.__class__.__name__, base_url=config.base_url
        )

    async def _handle_request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        # Logging request hanya jika self.debug (config klien) adalah True
        if self.debug:
            headers = kwargs.get("headers", self.client.headers)
            self.log.debug(
                f"HTTP {method} {url} | headers={dict(headers)} | kwargs={kwargs}"
            )

        try:
            response = await getattr(self.client, method.lower())(url, **kwargs)
            response.raise_for_status()

            # Logging response hanya jika self.debug adalah True
            if self.debug:
                self.log.debug(
                    f"Response [{response.status_code}] | headers={dict(response.headers)} | "
                    f"body={response.text[:300]}"
                )

        except httpx.HTTPStatusError as exc:
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

        except httpx.RequestError as exc:
            self.log.error(f"Connection Error: {exc.__class__.__name__}")
            raise HTTPConnectionError(
                message=f"Connection error to external service: {exc.__class__.__name__}",
                context={
                    "url": str(exc.request.url) if exc.request else url,
                    "request_headers": dict(exc.request.headers)
                    if exc.request
                    else None,
                },
                cause=exc,
            ) from exc

        return response

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._handle_request("GET", url, **kwargs)

    # Fungsi baru yang menggabungkan Panggil dan Normalisasi
    async def _call_and_normalize(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Eksekusi HTTP call dan normalisasi hasilnya ke dict standar."""
        raw_response = await self._handle_request(method, endpoint, **kwargs)

        # Meneruskan self.debug ke utilitas normalisasi
        normalized_data = response_to_normalized_dict(
            response=raw_response, debug=self.debug
        )

        return normalized_data
