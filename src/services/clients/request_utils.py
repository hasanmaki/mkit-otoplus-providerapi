"""module utilitas


hanya wrapper untuk get post dan lain lain
dan agnostik terhadap client , baik itu disipos / isimple.
"""

from typing import Any

import httpx
from httpx import AsyncClient, Response
from loguru import logger

from src.custom.exceptions import HTTPConnectionError


async def safe_fetch(
    client: AsyncClient,
    method: str,
    url: str,
    log_context: str,
    **kwargs: Any,
) -> Response:
    """
    Wrapper generik untuk eksekusi httpx yang hanya menangani RequestError (koneksi/timeout).

    Catatan: Error Status HTTP (4xx/5xx) harus ditangani di lapisan DigiposResponse.
    """
    local_log = logger.bind(service=log_context)

    try:
        local_log.debug(f"Issuing {method} request to {url}")
        http_response = await getattr(client, method.lower())(url, **kwargs)

        return http_response

    except httpx.RequestError as exc:
        local_log.error(
            f"Connection Error to {url}: {exc.__class__.__name__}", exception=exc
        )
        raise HTTPConnectionError(
            message=f"Connection error to external service: {exc.__class__.__name__}",
            context={"url": url, "details": str(exc)},
            cause=exc,
        ) from exc
