from typing import Any, Dict, Optional

import httpx
from loguru import logger

from src.config.settings import AppSettings
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


def _build_meta_info(response: httpx.Response, debug: bool = False) -> Dict[str, Any]:
    """
    Buat meta info minimal atau lengkap, tergantung debug mode.
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
                h: v for h, v in response.headers.items() if h.lower().startswith("x-")
            },
        })

    return meta


def response_upstream_to_dict(
    response: httpx.Response,
    settings: Optional[AppSettings] = None,
    *,
    debug_override: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Normalisasi response dari API target:
    - Tangani JSON/text fallback
    - Standarisasi struktur output
    - Meta minimal + bisa auto-expand kalau debug aktif

    Output:
    {
        "api_status_code": int,
        "meta": dict[str, Any],
        "data": Any
    }
    """
    data = _parse_response_body(response)
    if data in (None, ""):
        logger.warning(f"Empty response body from {response.request.url}")
        raise HttpResponseError(
            message="Provider returned empty response body",
            context={
                "status_code": response.status_code,
                "url": str(response.request.url),
                "raw": response.text,
            },
        )

    # --- tentukan apakah debug aktif ---
    if debug_override is not None:
        debug_mode = debug_override
    elif settings is not None:
        debug_mode = getattr(settings.application, "debug", False)
    else:
        debug_mode = False

    # --- bangun meta sesuai mode ---
    meta = _build_meta_info(response, debug=debug_mode)

    # --- hasil akhir ---
    return {
        "api_status_code": response.status_code,
        "meta": meta,
        "data": data,
    }
