import httpx

from src.config.constant import ResponseMessage

# ----------------------------------------------------------
# Internal parser functions (safe)
# ----------------------------------------------------------


def _parse_json(resp: httpx.Response) -> tuple[str, dict]:
    """Parse JSON response, fallback ke text/empty jika decoding error."""
    try:
        body = resp.json()
        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
    except httpx.DecodingError:
        # fallback ke text
        return _parse_text_safe(resp)
    except Exception:
        return ResponseMessage.UNKNOWN, {
            "raw": resp.text if hasattr(resp, "text") else None
        }
    return ResponseMessage.PRIMITIVE, {"raw": body}


def _parse_text_safe(resp: httpx.Response) -> tuple[str, dict]:
    """Parse text/html response dengan safe guard decoding errors."""
    try:
        text = resp.text.strip()
        if not text:
            return ResponseMessage.EMPTY_BODY, {"raw": None}
    except Exception:
        return ResponseMessage.UNKNOWN, {"raw": None}
    return ResponseMessage.TEXT, {"raw": text}


# ----------------------------------------------------------
# Exposed function for HttpClientService
# ----------------------------------------------------------


def parse_response(resp: httpx.Response) -> tuple[str, dict]:
    """Auto detect content-type dan parse responsenya dengan safe fallback."""
    ctype = resp.headers.get("content-type", "").lower() if resp.headers else ""

    try:
        if "json" in ctype:
            return _parse_json(resp)
        if "text" in ctype or "html" in ctype:
            return _parse_text_safe(resp)

        # fallback untuk semua content-type lain
        return _parse_text_safe(resp)
    except Exception:
        return ResponseMessage.UNKNOWN, {"raw": None}
