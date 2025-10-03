from typing import Any

import httpx


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
    """Standarisasi bentuk response."""
    return {
        "status_code": response.status_code,
        "content_length": _get_content_length(response),
        "meta": {},  # bisa ditambah info trace_id, duration, dll
        "data": _parse_response_body(response),
    }
