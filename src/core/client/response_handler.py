from typing import Any

import httpx
from loguru import logger

from src.config.constant import ResponseMessage


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
