# src/core/client/http_service.py
from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

import httpx
from loguru import logger

from src.config.constant import ResponseMessage
from src.custom.exceptions import HTTPConnectionError, HttpResponseError

# --- Type Alias untuk parser function ---
ParserFunc = Callable[[httpx.Response], tuple[str, dict[str, Any]]]


# ============================================================
# Default Parsers (Strategy)
# ============================================================


def _parse_json(resp: httpx.Response) -> tuple[str, dict[str, Any]]:
    try:
        body = resp.json()
        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        elif isinstance(body, list):
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
        else:
            return ResponseMessage.PRIMITIVE, {"raw": body}
    except Exception:
        text = resp.text.strip()
        if text:
            return ResponseMessage.TEXT, {"raw": text}
        return ResponseMessage.EMPTY_BODY, {"raw": None}


def _parse_text(resp: httpx.Response) -> tuple[str, dict[str, Any]]:
    text = resp.text.strip()
    if not text:
        return ResponseMessage.EMPTY_BODY, {"raw": None}
    return ResponseMessage.TEXT, {"raw": text}


# ============================================================
# Model
# ============================================================


@dataclass
class NormalizedResponse:
    status_code: int
    url: str
    meta: dict[str, Any]
    message: str
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ============================================================
# Core Client (Context)
# ============================================================


class HttpClientService:
    """HTTP client dengan parser berbasis content-type (Strategy Pattern)."""

    _content_type_parsers: dict[str, ParserFunc] = {
        "application/json": _parse_json,
        "text/*": _parse_text,  # semua text/html, text/plain dll
    }
    _default_parser: ParserFunc = _parse_text

    def __init__(
        self,
        client: httpx.AsyncClient,
        service_name: str | None = None,
        default_parser: ParserFunc | None = None,
    ):
        inferred_name = service_name or getattr(client.base_url, "host", "Upstream")
        self.client = client
        self.log = logger.bind(service=inferred_name)

        # override parser default kalau dikasih
        if default_parser:
            self._default_parser = default_parser

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def safe_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any]:
        """Use this."""
        try:
            resp = await self._request(method, endpoint, **kwargs)
            normalized = self._normalize(resp)
            return normalized.to_dict()
        except Exception as exc:
            self.log.error(f"Safe request failed: {exc}")
            return NormalizedResponse(
                0, endpoint, {}, ResponseMessage.INTERNAL_ERROR, {"error": str(exc)}
            ).to_dict()

    # ------------------------------------------------------------------
    # Request layer
    # ------------------------------------------------------------------

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Low-level HTTP request wrapper."""
        if method.upper() not in ["GET", "POST"]:
            raise ValueError(f"Invalid HTTP method: {method}")

        try:
            self.log.debug(f"Issuing {method} request to {endpoint}")
            resp = await getattr(self.client, method.lower())(endpoint, **kwargs)
            resp.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPConnectionError(
                message="Connection error",
                context={"endpoint": endpoint, "details": str(exc)},
                cause=exc,
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise HttpResponseError(
                message=f"Bad status {exc.response.status_code}",
                context={"endpoint": endpoint, "text": exc.response.text},
                cause=exc,
            ) from exc
        return resp

    # ------------------------------------------------------------------
    # Normalize Layer
    # ------------------------------------------------------------------

    def _normalize(
        self, resp: httpx.Response, *, debug: bool = False
    ) -> NormalizedResponse:
        """Pilih parser sesuai content-type dan normalisasi hasil response."""
        try:
            url = str(resp.request.url.copy_with(query=None))
            method = resp.request.method
            status = resp.status_code
            content_type: str = resp.headers.get(
                "content-type", "application/octet-stream"
            )

            # pilih parser sesuai content type
            parser = self._get_parser(content_type)
            msg, data = parser(resp)

            meta = {}
            if debug:
                meta = {
                    "method": method,
                    "headers": dict(resp.headers),
                    "elapsed": getattr(resp.elapsed, "total_seconds", lambda: None)(),
                    "http_version": getattr(resp, "http_version", "unknown"),
                }

            payload_type = type(data).__name__
            payload_size = len(str(data))
            self.log.debug(
                f"{method} {url} -> {status} | ctype={content_type} | type={payload_type}, size={payload_size}"
                + (f" | preview={str(data)[:200]}..." if debug else "")
            )

            return NormalizedResponse(status, url, meta, msg, data)
        except Exception as exc:
            self.log.error(f"Normalize failed: {exc}")
            return NormalizedResponse(
                0, "unknown", {}, ResponseMessage.INTERNAL_ERROR, {"raw": str(exc)}
            )

    # ------------------------------------------------------------------
    # Parser Registry & Selector
    # ------------------------------------------------------------------

    def register_parser(self, content_type: str, parser: ParserFunc) -> None:
        """Daftarkan parser custom untuk content-type tertentu."""
        self._content_type_parsers[content_type.lower()] = parser

    def _get_parser(self, content_type: str) -> ParserFunc:
        """Pilih parser sesuai content-type (support wildcard)."""
        main_type = content_type.split(";")[0].strip().lower()
        if main_type in self._content_type_parsers:
            return self._content_type_parsers[main_type]

        # wildcard match (application/* atau text/*)
        main_category = main_type.split("/")[0]
        wildcard_key = f"{main_category}/*"
        if wildcard_key in self._content_type_parsers:
            return self._content_type_parsers[wildcard_key]

        # default fallback
        return self._default_parser
