from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from src.core.client.service_parser import parse_response

T = TypeVar("T")


class ApiRawResponse[T](BaseModel):
    status_code: int
    content_type: str | None
    meta: dict[str, Any]
    body_type: str
    data: T


def normalize_response(
    resp: httpx.Response, debugresponse: bool = False
) -> ApiRawResponse:
    """Normalize hasil parse menjadi ApiRawResponse Pydantic."""
    body_type, raw_data = parse_response(resp)
    meta = {}
    if debugresponse:
        meta = {
            "headers": dict(getattr(resp, "headers", {})),
            "elapsed": getattr(resp.elapsed, "total_seconds", lambda: None)()
            if hasattr(resp, "elapsed")
            else None,
        }

    return ApiRawResponse(
        status_code=getattr(resp, "status_code", 0),
        content_type=resp.headers.get("content-type") if resp.headers else None,
        meta=meta,
        body_type=body_type,
        data=raw_data,
    )
