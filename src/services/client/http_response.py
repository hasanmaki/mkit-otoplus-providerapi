from typing import Any

import httpx
from loguru import logger
from pydantic import BaseModel, Field

from services.client.sch_response import ResponseMessage
from utils.log_utils import logger_wraps, timeit


class ApiRawResponse(BaseModel):
    """Kontrak respons mentah yang jelas, siap dikonsumsi layer 1."""

    # Field top-level
    url: str
    path: str | None
    status_code: int

    # Meta tambahan (non-duplikat)
    meta: dict[str, Any] = Field(default_factory=dict)

    # Data parsed dari body
    data: Any

    # Deskripsi status / error handling
    description: str = "httpx.resp to layer 1 ok"


class HttpResponseService:
    """Parser utama: httpx.Response → ApiRawResponse."""

    def __init__(self, resp: httpx.Response, debug: bool = False):
        self.resp = resp
        self.debug = debug
        self.last_error: str | None = None

    # ------------------ Pure parser helpers ------------------
    def _try_parse_json(self) -> tuple[str, dict[str, Any] | Any]:
        try:
            body = self.resp.json()
        except Exception as e:
            raise ValueError(f"Invalid JSON: {e}") from e

        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
        return ResponseMessage.PRIMITIVE, {"raw": body}

    def _try_parse_text(self) -> tuple[str, dict[str, Any]]:
        text = (self.resp.text or "").strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
        return ResponseMessage.TEXT, {"raw": text}

    # ------------------ Main parser ------------------
    @timeit
    def parse_body(self) -> tuple[str, dict[str, Any] | Any]:
        """Fallback chain: JSON → TEXT → ERROR."""
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
            try:
                return parser()
            except Exception as e:
                self.last_error = str(e)

        # gagal total
        return ResponseMessage.ERROR, {
            "error": self.last_error or "Unknown parsing error",
            "raw": self.resp.text[:500] if self.resp.text else None,
        }

    # ------------------ Meta helpers ------------------
    def _get_core_meta(self) -> dict[str, Any]:
        resp = self.resp
        return {
            "reason_phrase": resp.reason_phrase,
            "elapsed_time_s": getattr(
                getattr(resp, "elapsed", None), "total_seconds", lambda: None
            )(),
            "content_type": resp.headers.get("content-type"),
        }

    def _get_api_raw_response_fields(self) -> dict[str, Any]:
        resp = self.resp
        return {
            "url": str(resp.url),
            "path": getattr(resp.url, "path", None),
            "status_code": resp.status_code,
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

    # ------------------ Public API ------------------
    @logger_wraps(level="DEBUG")
    @timeit
    def to_dict(self) -> ApiRawResponse:
        # top-level fields
        top_fields = self._get_api_raw_response_fields()

        # meta
        meta = self._get_core_meta()
        if self.debug:
            meta.update(self._get_debug_meta())

        # parse body
        body_type, parsed_data = self.parse_body()
        meta["body_type"] = body_type

        # deskripsi status
        if body_type == ResponseMessage.ERROR:
            description = self.last_error or "Unknown parsing error"
            # pindahkan info top-level ke parsed_data agar tidak hilang
            parsed_data.update(top_fields)
        else:
            description = "httpx.resp to layer 1 ok"

        logger.debug(f"Parsing mode debug={self.debug}, body_type={body_type}")

        return ApiRawResponse(
            **top_fields,
            meta=meta,
            data=parsed_data,
            description=description,
        )


class ResponseParserFactory:
    """Factory agar bisa diinject via dependency FastAPI."""

    def __init__(self, parser_cls: type[HttpResponseService] = HttpResponseService):
        self.parser_cls = parser_cls

    def __call__(self, resp: httpx.Response, debug: bool = False) -> ApiRawResponse:
        return self.parser_cls(resp, debug).to_dict()


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Wrapper simple (non-DI usecase)."""
    return HttpResponseService(resp, debugresponse).to_dict().model_dump()
