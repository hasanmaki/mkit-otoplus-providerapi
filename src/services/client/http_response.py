from typing import Any

import httpx
from loguru import logger

from services.client.sch_response import ResponseMessage
from utils.log_utils import logger_wraps, timeit


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
        try:
            body = self.resp.json()
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}") from e

        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
        return ResponseMessage.PRIMITIVE, {"raw": body}

    def _try_parse_text(self) -> tuple[ResponseMessage, dict[str, Any]]:
        text = (self.resp.text or "").strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
        return ResponseMessage.TEXT, {"raw": text}

    # ============================================================
    #  MAIN PARSER LOGIC
    # ============================================================
    @timeit
    def parse_body(self) -> tuple[ResponseMessage, dict[str, Any] | Any]:
        """Fallback chain: JSON → TEXT → ERROR."""
        content_type = (self.resp.headers.get("content-type") or "").lower()

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
            "raw": self.resp.text[:500]
            if self.resp.text
            else None,  # kasih potongan isi
        }

    # ============================================================
    #  META HELPERS
    # ============================================================
    def _get_core_meta(self) -> dict[str, Any]:
        resp = self.resp
        return {
            "url": str(resp.url),
            "host": getattr(resp.url, "host", None),
            "path": getattr(resp.url, "path", None),
            "status_code": resp.status_code,
            "reason_phrase": resp.reason_phrase,
            "elapsed_time_s": getattr(resp.elapsed, "total_seconds", lambda: None)(),
            "content_type": resp.headers.get("content-type"),
        }

    def _get_debug_meta(self) -> dict[str, Any]:
        resp = self.resp
        req = getattr(resp, "request", None)
        return {
            "method": getattr(req, "method", None),
            "request_headers": dict(getattr(req, "headers", {})),
            "response_headers": dict(resp.headers),
            "response_history": [dict(r.headers) for r in resp.history],
            "response_cookies": dict(resp.cookies),
        }

    # ============================================================
    #  PUBLIC API
    # ============================================================
    @logger_wraps(level="DEBUG")
    @timeit
    def to_dict(self) -> dict[str, Any]:
        """Return dict(meta, data) siap dipakai service layer."""
        meta = self._get_core_meta()
        if self.debug:
            meta.update(self._get_debug_meta())

        body_type, parsed_data = self.parse_body()
        meta["body_type"] = body_type
        logger.debug(f"the mode: -> {self.debug}")
        return {"meta": meta, "data": parsed_data}


# ============================================================
#  FACTORY CLASS + WRAPPER FUNCTION
# ============================================================
class ResponseParserFactory:
    """Factory agar bisa diinject via dependency FastAPI."""

    def __init__(self, parser_cls: type[HttpResponseService] = HttpResponseService):
        self.parser_cls = parser_cls

    def __call__(self, resp: httpx.Response, debug: bool = False) -> dict[str, Any]:
        """Callable agar bisa langsung dipakai di service layer."""
        return self.parser_cls(resp, debug).to_dict()


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Wrapper simple (non-DI usecase)."""
    return HttpResponseService(resp, debugresponse).to_dict()
