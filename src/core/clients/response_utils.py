# src/core/clients/response_utils.py
import json
from typing import Any, Type, TypeVar

import httpx
from fastapi.responses import PlainTextResponse
from loguru import logger
from pydantic import ValidationError

from src.config.settings import AppSettings
from src.custom.exceptions import HttpResponseError

T = TypeVar("T")


def _parse_response_body(response: httpx.Response) -> Any:
    """
    Safely parse response body.
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


def _get_content_length(response: httpx.Response) -> int | None:
    """Ambil header content-length (kalau ada & valid integer)."""
    content_length_str = response.headers.get("content-length")
    if content_length_str and content_length_str.isdigit():
        return int(content_length_str)
    return None


def _get_meta_info(response: httpx.Response) -> dict[str, Any] | None:
    """Kumpulin semua header yang dimulai dengan x- (case-insensitive)."""
    metainfo = {}
    for header, value in response.headers.items():
        if header.lower().startswith("x-"):
            metainfo[header] = value
    return metainfo or None


def normalized_response(response: httpx.Response) -> dict[str, Any]:
    """
    Standarisasi bentuk response API external.
    Output:
        {
            "status_code": int,
            "content_length": int | None,
            "meta": dict[str, Any] | None,
            "data": Any
        }
    """
    data = _parse_response_body(response)
    content_length = _get_content_length(response)
    meta = _get_meta_info(response)

    if not data:
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
        "status_code": response.status_code,
        "content_length": content_length,
        "meta": meta,
        "data": data,
    }


def to_text_response_simple(obj: Any) -> str:
    """
    Convert dict / Pydantic model ke format key=value&key2=value2
    - 'data' → langsung di-dump JSON (nggak di-flatten)
    - dict nested (misal meta) → di-flatten pakai dot notation
    """
    # handle pydantic v1/v2
    if hasattr(obj, "model_dump"):
        obj = obj.model_dump()
    elif hasattr(obj, "dict"):
        obj = obj.dict()

    parts = []

    for k, v in obj.items():
        if k == "data":
            # stringify seluruh data agar ngga rusak kalau tipe nested
            v = json.dumps(v, separators=(",", ":"))
        elif isinstance(v, dict):
            # flatten meta dict
            for sub_k, sub_v in (v or {}).items():
                parts.append(f"{k}.{sub_k}={sub_v}")
            continue
        parts.append(f"{k}={v}")

    return "&".join(parts)


def respond(obj: Any, settings: AppSettings) -> Any:
    """
    Centralized response helper:
    - kalau settings.digipos.response.type == "text" → PlainTextResponse
    - default → JSON (FastAPI handle otomatis)
    """
    response_type = getattr(settings.digipos.response.type, "lower", lambda: "")()
    if response_type == "text":
        return PlainTextResponse(to_text_response_simple(obj))
    return obj


def safe_convert(model: Type[T], data: Any) -> T | dict:
    try:
        return model(**data)
    except ValidationError as e:
        logger.error(
            f"[safe_convert] Failed to parse {model.__name__}: {e.errors() if hasattr(e, 'errors') else e}"
        )
        logger.debug(f"[safe_convert] Raw data: {data}")
        return data
