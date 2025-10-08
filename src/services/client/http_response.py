from typing import Any

import httpx

from services.client.sch_response import ApiResponseIN, ResponseMessage
from utils.log_utils import logger_wraps, timeit


class HttpResponseService:
    """Parser utama: httpx.Response → ApiResponseIN (flat, clean)."""

    def __init__(self, resp: httpx.Response, debug: bool = False):
        self.resp = resp
        self.debug = debug
        self.last_error: str | None = None

    def _try_parse_json(self) -> tuple[str, Any]:
        """Inner Parser Helper.

        Parser untuk JSON. dengan Urutan Fallbak:
            1- JSON → DICT

        Returns:
            tuple[str, Any]:
                - ResponseMessage.DICT → dict
        """
        try:
            body = self.resp.json()
        except Exception as e:
            self.last_error = f"Invalid JSON: {e}"
            return ResponseMessage.ERROR, {
                "error": self.last_error,
                "raw": self.resp.text[:500] if self.resp.text else None,
            }

        return ResponseMessage.DICT, body if isinstance(body, dict) else {"raw": body}

    def _try_parse_text(self) -> tuple[str, Any]:
        text = (self.resp.text or "").strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
        return ResponseMessage.TEXT, {"raw": text}

    @timeit
    def parse_body(self) -> tuple[str, Any]:
        """Fallback chain: JSON → TEXT → ERROR.

        # ------------------ Main parser ------------------
        """
        content_type = (self.resp.headers.get("content-type") or "").lower()
        try:
            if "json" in content_type:
                return self._try_parse_json()
            if any(x in content_type for x in ["text", "html", "xml"]):
                return self._try_parse_text()
        except Exception as e:
            self.last_error = f"Parsing failed ({content_type}): {e}"

        # fallback universal
        for parser in (self._try_parse_json, self._try_parse_text):
            response_type, data = parser()
            if response_type != ResponseMessage.ERROR:
                return response_type, data

        # gagal total
        return ResponseMessage.ERROR, {
            "error": self.last_error or "Unknown parsing error",
            "raw": self.resp.text[:500] if self.resp.text else None,
        }

    def _get_flat_meta(self, response_type: str) -> dict[str, Any]:
        """# ------------------ Meta helpers ------------------."""
        resp = self.resp
        req = getattr(resp, "request", None)
        meta = {
            "status_code": resp.status_code,
            "elapsed_time_s": getattr(
                getattr(resp, "elapsed", None), "total_seconds", lambda: None
            )(),
            "content_type": resp.headers.get("content-type"),
        }
        if self.debug:
            meta.update({
                "request_headers": dict(getattr(req, "headers", {})) if req else {},
                "response_headers": dict(resp.headers),
                "url": str(resp.url),
                "path": getattr(resp.url, "path", None),
            })
        # optional info yang sebelumnya ada sebagai field
        meta.update({
            "response_type": response_type,
            "description": self.last_error
            if response_type == ResponseMessage.ERROR
            else "ok",
        })
        return meta

    @logger_wraps(level="DEBUG")
    @timeit
    def to_dict(self) -> ApiResponseIN:
        """# ------------------ Public API ------------------."""
        response_type, parsed_data = self.parse_body()
        meta = self._get_flat_meta(response_type)

        return ApiResponseIN(
            status_code=self.resp.status_code,
            url=str(self.resp.url.host),
            debug=self.debug,
            meta=meta,
            raw_data=parsed_data,
        )


class ResponseParserFactory:
    """Factory agar bisa diinject via dependency FastAPI."""

    def __init__(self, parser_cls: type[HttpResponseService] = HttpResponseService):
        self.parser_cls = parser_cls

    def __call__(self, resp: httpx.Response, debug: bool = False) -> ApiResponseIN:
        return self.parser_cls(resp, debug).to_dict()


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Wrapper simple (non-DI usecase)."""
    return HttpResponseService(resp, debugresponse).to_dict().model_dump()
