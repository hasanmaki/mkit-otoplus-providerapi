from dataclasses import asdict
from typing import Any

import httpx
from loguru import logger

from services.client.model import ApiResponseIN, ResponseType
from src.custom.exceptions import HttpResponseError
from utils.log_utils import timeit


class HttpResponseService:
    """Convert httpx.Response → ApiResponseIN (flat, minimal, safe)."""

    def __init__(self, resp: httpx.Response, debug: bool = False):
        self.resp = resp
        self.debug = debug
        self.last_error: str | None = None
        self.log = logger.bind(url=str(resp.url), debug=debug)

    def _try_parse_json(self) -> tuple[str, Any]:
        """Error json tidak di raise , tetapi ada flag yang bisa di consume layer selanjut nya."""
        try:
            body = self.resp.json()
            return ResponseType.DICT, body if isinstance(body, dict) else {"raw": body}
        except Exception as e:
            self.last_error = f"Invalid JSON: {e}"
            return ResponseType.ERROR, {
                "parse_error": True,
                "error": str(e),
                "raw": self.resp.text[:500] or None,
            }

    def _try_parse_text(self) -> tuple[str, Any]:
        text = (self.resp.text or "").strip()
        if not text:
            return ResponseType.EMPTY, {"raw": None}
        return ResponseType.TEXT, {"raw": text}

    @timeit
    def parse_body(self) -> tuple[str, Any]:
        content_type = (self.resp.headers.get("content-type") or "").lower()

        # 🔒 JSON-only mode (fail-fast)
        if "json" not in content_type:
            raise HttpResponseError(
                message=f"[HttpResponseService] Expected JSON content type, got: {content_type or 'unknown'}",
                context={"content": content_type},
            )

        return self._try_parse_json()

    def _build_meta(self, response_type: str) -> dict[str, Any]:
        if not self.debug:
            return {"with_meta": False}

        resp = self.resp
        req = getattr(resp, "request", None)

        description = self.last_error or "ok"

        return {
            "with_meta": True,
            "elapsed_s": getattr(
                getattr(resp, "elapsed", None), "total_seconds", lambda: None
            )(),
            "request_headers": dict(getattr(req, "headers", {})) if req else {},
            "response_headers": dict(resp.headers),
            "method": getattr(req, "method", None) if req else None,
            "path": getattr(resp.url, "path", None),
            "trace_id": resp.headers.get("x-trace-id"),
            "request_id": resp.headers.get("x-request-id"),
            "response_type": response_type,
            "description": description,
        }

    @timeit
    def to_response_in(self) -> ApiResponseIN:
        """Parse & wrap to ApiResponseIN."""
        response_type, parsed = self.parse_body()
        meta = self._build_meta(response_type)
        return ApiResponseIN(
            status_code=self.resp.status_code,
            url=str(self.resp.url.host),
            path=str(self.resp.url.path),
            debug=self.debug,
            meta=meta,
            raw_data=parsed,
        )


class ResponseHandlerFactory:
    """Factory buat DI, auto-handle json parse error & safe fallback."""

    def __init__(
        self,
        parser_cls: type[HttpResponseService] = HttpResponseService,
        strict: bool = False,
    ):
        self.parser_cls = parser_cls
        self.strict = strict

    def __call__(self, resp: httpx.Response, debug: bool = False) -> ApiResponseIN:
        try:
            parsed = self.parser_cls(resp, debug).to_response_in()

        except HttpResponseError as e:
            # misal bukan JSON / upstream kacau
            if self.strict:
                raise
            logger.warning(f"[ResponseParserFactory] JSON parse failed → fallback: {e}")
            return ApiResponseIN(
                status_code=resp.status_code,
                url=str(resp.url.host),
                path=str(resp.url.path),
                raw_data={"fallback_raw": resp.text[:500]},
                debug=debug,
                meta={"with_meta": False, "fallback_reason": str(e)},
            )
        return parsed


def response_to_dict(resp: httpx.Response, debug: bool = False) -> dict[str, Any]:
    """Quick helper buat manual call tanpa DI."""
    return asdict(HttpResponseService(resp, debug).to_response_in())
