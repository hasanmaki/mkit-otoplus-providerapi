import httpx
from loguru import logger

from src.config.cfg_api_clients import ApiBaseConfig
from src.custom.exceptions import HTTPConnectionError, HttpResponseError


class BaseApiClient:
    """Base class untuk mengelola klien HTTP eksternal."""

    def __init__(
        self, client: httpx.AsyncClient, config: ApiBaseConfig, debug: bool = False
    ):
        self.client = client
        self.config = config
        self.debug = debug
        self.log = logger.bind(
            client_name=self.__class__.__name__, base_url=config.base_url
        )

    async def _handle_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if self.debug:
            # log request headers + params/body
            headers = kwargs.get("headers", self.client.headers)
            self.log.debug(
                f"HTTP {method} {url} | headers={dict(headers)} | kwargs={kwargs}"
            )

        try:
            response = await getattr(self.client, method.lower())(url, **kwargs)
            response.raise_for_status()

            if self.debug:
                # log response status + headers + snippet body
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
