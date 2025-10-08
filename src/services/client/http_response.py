from enum import StrEnum
from typing import Any

import httpx

from utils.log_utils import timeit


class ResponseMessage(StrEnum):
    """Jenis hasil parsing body response."""

    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITIVE"
    EMPTY = "EMPTY"
    ERROR = "ERROR"


class HttpResponseService:
    """Parser utama untuk mengubah httpx.Response → dict(meta, data)."""

    def __init__(self, resp: httpx.Response, debug: bool = False):
        self.resp = resp
        self.debug = debug
        self.last_error: str | None = None

    # ============================================================
    #  PURE PARSER HELPERS
    # ============================================================
    def _try_parse_json(self) -> tuple[ResponseMessage, dict[str, Any] | Any]:
        body = self.resp.json()
        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
        return ResponseMessage.PRIMITIVE, {"raw": body}

    def _try_parse_text(self) -> tuple[ResponseMessage, dict[str, Any]]:
        text = self.resp.text.strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
        return ResponseMessage.TEXT, {"raw": text}

    # ============================================================
    #  MAIN PARSER LOGIC
    # ============================================================
    @timeit
    def parse_body(self) -> tuple[ResponseMessage, dict[str, Any] | Any]:
        """Fallback chain: JSON → TEXT → ERROR."""
        content_type = self.resp.headers.get("content-type", "").lower()

        # Berdasarkan Content-Type
        try:
            if "json" in content_type:
                return self._try_parse_json()
            if any(x in content_type for x in ["text", "html", "xml"]):
                return self._try_parse_text()
        except Exception as e:
            self.last_error = f"Parsing failed ({content_type}): {e}"

        # Fallback ke JSON → TEXT universal
        for parser in (self._try_parse_json, self._try_parse_text):
            try:
                return parser()
            except Exception as e:
                self.last_error = str(e)

        # Gagal total
        return ResponseMessage.ERROR, {
            "error": self.last_error or "Unknown parsing error",
            "raw": None,
        }

    # ============================================================
    #  META HELPERS
    # ============================================================
    def _get_core_meta(self) -> dict[str, Any]:
        resp = self.resp
        return {
            "url": str(resp.url),
            "host": resp.url.host,
            "path": resp.url.path,
            "status_code": resp.status_code,
            "reason_phrase": resp.reason_phrase,
            "elapsed_time_s": resp.elapsed.total_seconds(),
            "content_type": resp.headers.get("content-type"),
        }

    def _get_debug_meta(self) -> dict[str, Any]:
        resp = self.resp
        return {
            "method": resp.request.method if resp.request else None,
            "request_headers": dict(resp.request.headers) if resp.request else None,
            "response_headers": dict(resp.headers),
            "response_history": [dict(r.headers) for r in resp.history],
            "response_cookies": dict(resp.cookies),
        }

    # ============================================================
    #  PUBLIC API
    # ============================================================
    @timeit
    def to_dict(self) -> dict[str, Any]:
        """Return dict(meta, data) yang siap dipakai service layer."""
        meta = self._get_core_meta()
        if self.debug:
            meta.update(self._get_debug_meta())

        body_type, parsed_data = self.parse_body()
        meta["body_type"] = body_type

        return {"meta": meta, "data": parsed_data}


# ============================================================
#  FACTORY CLASS + WRAPPER FUNCTION
# ============================================================
class ResponseParserFactory:
    """Factory agar bisa diinject via dependency FastAPI."""

    def __init__(self, parser_cls: type[HttpResponseService] = HttpResponseService):
        self.parser_cls = parser_cls

    def __call__(self, resp: httpx.Response, debug: bool = False) -> dict[str, Any]:
        return self.parser_cls(resp, debug).to_dict()


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Wrapper simpel (non-DI usecase)."""
    return HttpResponseService(resp, debugresponse).to_dict()
