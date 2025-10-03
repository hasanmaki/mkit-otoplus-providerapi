# src/core/clients/response_utils.py
from typing import Any

import httpx

from src.custom.exceptions import HttpResponseError


def _parse_response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def _get_content_length(response: httpx.Response) -> int | None:
    content_length_str = response.headers.get("content-length")
    if content_length_str and content_length_str.isdigit():
        return int(content_length_str)
    return None


def normalized_response(response: httpx.Response) -> dict[str, Any]:
    """Standarisasi response + early validation."""
    data = _parse_response_body(response)
    content_length = _get_content_length(response)

    # ✅ kalau body kosong / None → langsung raise
    if not data:
        raise HttpResponseError(
            message="Provider returned empty response body",
            context={
                "status_code": response.status_code,
                "url": str(response.request.url),
                "raw": response.text,
            },
        )

    return {
        "status_code": response.status_code,
        "content_length": content_length,
        "meta": {},  # bisa isi trace_id, request_id, dsb
        "data": data,
    }
