from enum import StrEnum

import httpx


class ResponseMessage(StrEnum):
    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITVE"
    INTERNAL_ERROR = "ERROR"
    EMPTY_BODY = "NONE"
    UNKNOWN = "UNKNOWN"


def _parse_json(resp: httpx.Response) -> tuple[str, dict]:
    try:
        body = resp.json()
        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
    except httpx.DecodingError:
        return _parse_text_safe(resp)
    except Exception:
        return ResponseMessage.UNKNOWN, {"raw": getattr(resp, "text", None)}
    return ResponseMessage.PRIMITIVE, {"raw": body}


def _parse_text_safe(resp: httpx.Response) -> tuple[str, dict]:
    try:
        text = resp.text.strip()
        if not text:
            return ResponseMessage.EMPTY_BODY, {"raw": None}
    except Exception:
        return ResponseMessage.UNKNOWN, {"raw": None}
    return ResponseMessage.TEXT, {"raw": text}


def parse_response(resp: httpx.Response) -> tuple[str, dict]:
    """Auto detect content-type dan parsing raw response."""
    ctype = resp.headers.get("content-type", "").lower() if resp.headers else ""
    try:
        if "json" in ctype:
            return _parse_json(resp)
        if "text" in ctype or "html" in ctype:
            return _parse_text_safe(resp)
        return _parse_text_safe(resp)
    except Exception:
        return ResponseMessage.UNKNOWN, {"raw": None}
