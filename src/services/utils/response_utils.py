from typing import Any, Dict

import httpx
from loguru import logger

from src.custom.exceptions import HttpResponseError


def parse_response_body(response: httpx.Response) -> Any:
    """
    Parse isi body dari httpx.Response:
    - Coba JSON → dict/list
    - Kalau bukan JSON, fallback ke text
    - Kalau JSON tapi bukan dict/list, wrap {"raw": data}
    """
    try:
        data = response.json()
        if isinstance(data, (dict, list)):
            return data
        return {"raw": data}
    except ValueError:
        return response.text


def build_meta_info(response: httpx.Response, *, debug: bool = False) -> Dict[str, Any]:
    """
    Bangun meta info response:
    - Minimal: url + method
    - Kalau debug=True → tambah info detail (elapsed, host, headers x-*)
    """
    meta: Dict[str, Any] = {
        "url": str(response.request.url),
        "method": response.request.method,
    }

    if debug:
        meta.update({
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "elapsed_ms": response.elapsed.total_seconds() * 1000,
            "host": response.request.url.host,
            "headers": {
                k: v for k, v in response.headers.items() if k.lower().startswith("x-")
            },
        })

    return meta


def response_to_normalized_dict(
    response: httpx.Response,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """
    Normalisasi response upstream ke struktur standar:
    {
        "api_status_code": int,
        "meta": dict,
        "data": Any
    }
    """
    data = parse_response_body(response)

    # --- validasi isi ---
    if data in (None, ""):
        # Logging di sini hanya untuk kondisi ERROR/WARNING
        logger.warning(f"Empty response body from {response.request.url}")
        raise HttpResponseError(
            message="Provider returned empty response body",
            context={
                "status_code": response.status_code,
                "url": str(response.request.url),
                "raw": response.text,
            },
        )

    # --- bangun meta ---
    # build_meta_info menggunakan parameter debug yang baru
    meta = build_meta_info(response, debug=debug)

    # --- hasil akhir ---
    normalized = {
        "api_status_code": response.status_code,
        "meta": meta,
        "data": data,
    }

    # Logging debug dilakukan di sini untuk hasil normalisasi
    if debug:
        logger.debug(f"[response_to_normalized_dict] normalized={normalized}")

    return normalized
