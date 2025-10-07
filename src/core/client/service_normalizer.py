from typing import Any

import httpx
from pydantic import BaseModel

from src.core.client.service_parser import parse_response


class ApiRawResponse(BaseModel):
    status_code: int
    content_type: str | None
    url: str
    meta: dict[str, Any]
    message: str
    data: dict[str, Any]


def normalize_response(
    resp: httpx.Response, include_meta: bool = True
) -> ApiRawResponse:
    """Normalize hasil parse menjadi ApiRawResponse Pydantic."""
    message_type, raw_data = parse_response(resp)
    meta = {}
    if include_meta:
        meta = {
            "headers": dict(getattr(resp, "headers", {})),
            "elapsed": getattr(resp.elapsed, "total_seconds", lambda: None)()
            if hasattr(resp, "elapsed")
            else None,
        }

    return ApiRawResponse(
        status_code=getattr(resp, "status_code", 0),
        content_type=resp.headers.get("content-type") if resp.headers else None,
        url=str(getattr(getattr(resp, "request", None), "url", "")),
        meta=meta,
        message=message_type,
        data=raw_data,
    )
