from typing import Any

import httpx
from loguru import logger

from src.config.constant import ResponseMessage
from src.custom.exceptions import HTTPConnectionError, HttpResponseError


# below code just incase need explorasi atau lain lain nya.
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


def handle_response(response: httpx.Response, *, debug: bool = False) -> dict[str, Any]:
    """Normalize upstream response — selalu return format seragam."""
    log = logger.bind(service="ResponseHandler")

    try:
        url = str(response.request.url.copy_with(query=None))
        method = response.request.method
        status = response.status_code

        try:
            body = response.json()
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
            text = response.text.strip()
            if text:
                data = {"raw": text}
                msg = ResponseMessage.TEXT
            else:
                data = {"raw": None}
                msg = ResponseMessage.EMPTY_BODY

        meta = {}
        if debug:
            meta = {
                "method": method,
                "headers": dict(response.headers),
                "elapsed": getattr(response.elapsed, "total_seconds", lambda: None)(),
                "http_version": getattr(response, "http_version", "unknown"),
            }

        log.debug(f"{method} {url} -> {status} | normalized")

    except Exception as exc:
        # fallback total: jika handler sendiri error
        log.error(f"ResponseHandler crashed: {exc}")
        return {
            "status_code": getattr(response, "status_code", 0),
            "url": getattr(response, "url", "unknown"),
            "meta": {},
            "message": ResponseMessage.INTERNAL_ERROR,
            "data": {"raw": str(exc)},
        }
    return {
        "status_code": status,
        "url": url,
        "meta": meta,
        "message": msg,
        "data": data,
    }
