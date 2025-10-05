from typing import Any, Dict, Optional

import httpx
from loguru import logger

from src.config.settings import AppSettings
from src.custom.exceptions import HttpResponseError


# ==========================================================
# 1️⃣ Low-level util: parser
# ==========================================================
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


# ==========================================================
# 2️⃣ Low-level util: meta builder
# ==========================================================
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


# ==========================================================
# 3️⃣ High-level util: normalizer utama
# ==========================================================
def response_upstream_to_dict(
    response: httpx.Response,
    settings: Optional[AppSettings] = None,
    *,
    debug_override: Optional[bool] = None,
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
        logger.warning(f"Empty response body from {response.request.url}")
        raise HttpResponseError(
            message="Provider returned empty response body",
            context={
                "status_code": response.status_code,
                "url": str(response.request.url),
                "raw": response.text,
            },
        )

    # --- tentukan debug mode ---
    debug_mode = (
        debug_override
        if debug_override is not None
        else getattr(settings.application, "debug", False)
        if settings is not None
        else False
    )

    # --- bangun meta ---
    meta = build_meta_info(response, debug=debug_mode)

    # --- hasil akhir ---
    normalized = {
        "api_status_code": response.status_code,
        "meta": meta,
        "data": data,
    }

    logger.debug(f"[response_upstream_to_dict] normalized={normalized}")
    return normalized
