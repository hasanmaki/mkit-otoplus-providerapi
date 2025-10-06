import httpx
from loguru import logger

from src.custom.exceptions import HTTPConnectionError, HttpResponseError


async def request_handler(
    client: httpx.AsyncClient, methode: str, url: str, **kwargs
) -> httpx.Response:
    """Wrapper for easy call httpx."""
    log = logger.bind(service="RequestHandler")
    if methode not in ["GET"]:
        raise ValueError(f"Invalid HTTP method: {methode}")

    try:
        log.debug(f"Issuing {methode} request to {url}")
        http_response = await getattr(client, methode.lower())(url, **kwargs)
        http_response.raise_for_status()

    except httpx.RequestError as exc:
        log.error(f"Connection Error to {url}: {exc.__class__.__name__}")  # noqa: TRY400
        raise HTTPConnectionError(
            message=f"Connection error to external service: {exc.__class__.__name__}",
            context={"url": url, "details": str(exc)},
            cause=exc,
        ) from exc
    except httpx.HTTPStatusError as exc:
        log.error(f"Response Status Error: {exc.response.status_code}")  # noqa: TRY400
        raise HttpResponseError(
            message=f"External service responded with status {exc.response.status_code}",
            context={"url": url, "response_text": exc.response.text},
            cause=exc,
        ) from exc
    return http_response
