from collections.abc import Callable
from typing import Any

import httpx

from core.sch_response import ApiResponseGeneric
from src.config.settings import AppSettings


def _parse_response_body(response: httpx.Response) -> Any:
    """Helper function to safely parse the response body."""
    try:
        data = response.json()
    except ValueError:
        data = response.text
    return data


def _get_content_length(response: httpx.Response) -> int | None:
    """Helper function to safely get the content-length header."""
    content_length_str = response.headers.get("content-length")
    if content_length_str and content_length_str.isdigit():
        return int(content_length_str)
    return None


def _full_response(response: httpx.Response) -> dict[str, Any]:
    """Response full mode."""
    data = _parse_response_body(response)
    content_length = _get_content_length(response)

    meta = {
        "status_code": response.status_code,
        "content_length": content_length,
        "url": str(response.url),
        "headers": dict(response.headers),
        "content_type": response.headers.get("content-type"),
    }

    return {
        "status_code": response.status_code,
        "content_length": content_length,
        "meta": meta,
        "data": data,
    }


def _simple_response(response: httpx.Response) -> dict[str, Any]:
    """Response simple mode."""
    data = _parse_response_body(response)
    content_length = _get_content_length(response)

    return {
        "status_code": response.status_code,
        "content_length": content_length,
        "meta": {},
        "data": data,
    }


RespsFunc = Callable[[httpx.Response], dict[str, Any]]


def context_to_dict(settings: AppSettings, response: httpx.Response) -> dict[str, Any]:
    """Context for the response handler, using a strategy pattern."""
    strategies = {
        "full": _full_response,
        "simple": _simple_response,
    }
    strategy = strategies.get(settings.response.mode, _full_response)
    return strategy(response)


def context_to_model(
    settings: AppSettings, response: httpx.Response, model: Any
) -> ApiResponseGeneric[Any]:
    """Context for the response handler with model validation."""
    strategies = {
        "full": _full_response,
        "simple": _simple_response,
    }
    strategy = strategies.get(settings.response.mode, _full_response)
    response_dict = strategy(response)
    return model.model_validate(response_dict)
