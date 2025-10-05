from typing import Any, Dict

import httpx
from loguru import logger

from src.custom.exceptions import HttpResponseError


def _parse_response_body(response: httpx.Response) -> Any:
    """
    Safely parse response body:
    - Prefer JSON
    - Fallback ke text
    - Kalau JSON bukan dict/list, wrap dalam {"raw": data}
    """
    try:
        data = response.json()
        if isinstance(data, (dict, list)):
            return data
        return {"raw": data}
    except ValueError:
        return response.text


def _get_meta_info(response: httpx.Response) -> Dict[str, Any] | None:
    """
    Ambil semua header yang dimulai dengan x- (case-insensitive)
    dan optional info lain.
    """
    meta: Dict[str, Any] = {}

    # custom x-* headers
    for header, value in response.headers.items():
        if header.lower().startswith("x-"):
            meta[header] = value

    # tambahan info opsional
    meta["content_type"] = response.headers.get("Content-Type")
    meta["content_length"] = response.headers.get("Content-Length")
    meta["elapsed_ms"] = response.elapsed.total_seconds() * 1000
    meta["host"] = response.request.url.host
    meta["path"] = response.request.url.path
    meta["method"] = response.request.method

    return meta or None


def response_as_dict(response: httpx.Response) -> Dict[str, Any]:
    """
    Normalisasi response dari API target.
    Output standar:
    {
        "status_code_target": int,
        "meta": dict[str, Any] | None,
        "data": Any
    }
    """
    data = _parse_response_body(response)
    meta = _get_meta_info(response)

    if data is None or data == "":
        logger.warning(f"Empty response body from {response.request.url}")
        raise HttpResponseError(
            message="Provider returned empty response body",
            context={
                "status_code": response.status_code,
                "url": str(response.request.url),
                "raw": response.text,
            },
        )

    return {
        "status_code_target": response.status_code,
        "meta": meta,
        "data": data,
    }
