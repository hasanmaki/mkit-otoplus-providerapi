import json
from typing import Any, Dict

import httpx
from loguru import logger

from src.custom.exceptions import HttpResponseError


def _parse_content_body(response: httpx.Response) -> Dict[str, Any]:
    """Melakukan parsing konten body yang andal."""
    content_type = "JSON"
    try:
        data = response.json()
        if not isinstance(data, (dict, list)):
            data = {"raw_data": data}
    except json.JSONDecodeError:
        content_type = "Text/Other"
        data = {"raw_text_content": response.text}

    return {
        "http_status_code": response.status_code,
        "content_source": content_type,
        "raw_payload": data,
    }


def _validate_response_status(response: httpx.Response, log: "logger") -> None:
    """Memastikan status 2xx dan raise custom exception jika 4xx/5xx."""
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        log.error(f"Response Status Error: {exc.response.status_code}")
        raise HttpResponseError(
            message=f"External service responded with status {exc.response.status_code}",
            context={"url": str(exc.request.url), "response_text": exc.response.text},
            cause=exc,
        ) from exc


def normalize_http_response(response: httpx.Response) -> Dict[str, Any]:
    """
    Fungsi utama: Memproses httpx.Response mentah menjadi Dict yang terstandarisasi.
    Menangani status check, parsing, dan empty check.
    """
    log_context = logger.bind(
        client_url=str(response.request.url), http_status=response.status_code
    )

    # 1. Status Check (Raise HttpResponseError jika 4xx/5xx)
    _validate_response_status(response, log_context)

    # 2. Parsing dan Standarisasi Output
    parsed_data = _parse_content_body(response)
    data_payload = parsed_data["raw_payload"]

    # 3. Validasi Isi Body (Empty Check)
    if data_payload in (None, "", {}, []):
        log_context.warning("Empty response body after parsing.")
        raise HttpResponseError(
            message="Provider returned empty response body",
            context={
                "status_code": response.status_code,
                "url": str(response.request.url),
                "raw": response.text,
            },
        )

    return parsed_data
