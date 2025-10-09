from typing import TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError

from servicess.client.depre_cated_response_model import (
    ApiErrorParsing,
    ApiResponseIN,
    ApiResponseOUT,
    CleanAndParseStatus,
)
from src.custom.exceptions import HttpResponseError
from utils.log_utils import timeit

T = TypeVar("T", bound=BaseModel)


@timeit
def clean_validate_raw_dict_data[T: BaseModel](
    raw_response: ApiResponseIN,
    target_model: type[T] | None = None,
    auto_wrap_error: bool = True,
) -> ApiResponseOUT[T | ApiErrorParsing]:
    """Cleaner + parser generik untuk raw API response.

    Args:
        raw_response: Raw response dari HTTP/service.
        target_model: Pydantic model untuk validasi.
        auto_wrap_error: True → validasi error di-wrap jadi ErrorData; False → raise exception.

    Returns:
        ApiResponseOUT dengan T atau ErrorData.
    """

    def _build_response(
        cleaned_data: T | ApiErrorParsing,
        parse_status: CleanAndParseStatus,
        description: str | None = None,
    ) -> ApiResponseOUT[T | ApiErrorParsing]:
        return ApiResponseOUT[T | ApiErrorParsing](
            status_code=raw_response.status_code,
            url=raw_response.url,
            path=getattr(raw_response, "path", "-"),
            debug=raw_response.debug,
            meta=raw_response.meta.copy() if raw_response.meta else None,
            parse=parse_status,
            data=cleaned_data,
            description=description,
        )

    # --- No target model, auto skip ---
    if target_model is None:
        return _build_response(
            ApiErrorParsing(
                data=raw_response.raw_data,
            ),
            CleanAndParseStatus.SKIPPED,
            "No parser model provided",
        )

    # --- Try validate model ---
    try:
        clean_data = target_model.model_validate(raw_response.raw_data)
        return _build_response(
            clean_data, CleanAndParseStatus.SUCCESS, "Data berhasil di-parse"
        )

    except ValidationError as e:
        if auto_wrap_error:
            error_message = str(e)
            error_data = ApiErrorParsing(data=raw_response.raw_data)
            logger.bind(url=raw_response.url, model=target_model.__name__).warning(
                f"Validation failed: {e}"
            )
            return _build_response(
                error_data,
                CleanAndParseStatus.ERROR,
                f"Validation failed {error_message}",
            )
        else:
            raise HttpResponseError(
                message="Validation failed",
                status_code=raw_response.status_code,
                cause=e,
            ) from e


def dict_to_plaintext(data: dict) -> str:  # noqa: D103
    parts = []
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_value = "{" + dict_to_plaintext(value) + "}"
            parts.append(f"{key}={formatted_value}")
        elif isinstance(value, bool):
            parts.append(f"{key}={str(value).lower()}")
        else:
            parts.append(f"{key}={value!s}")
    return "&".join(parts).replace(" ", "")
