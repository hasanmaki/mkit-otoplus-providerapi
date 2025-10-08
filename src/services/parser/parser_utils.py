from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError

from services.client.response_model import (
    ApiResponseIN,
    ApiResponseOUT,
    CleanAndParseStatus,
)
from utils.log_utils import timeit


class ErrorData(BaseModel):  # Simple model for error data
    error_message: str
    raw_data: Any


T = TypeVar("T", bound=BaseModel)


@timeit
def clean_validate_raw_dict_data[T: BaseModel](
    raw_response: ApiResponseIN, target_model: type[T] | None = None
) -> ApiResponseOUT[T | ErrorData]:  # change return type
    """Generic cleaner + parser."""
    if target_model is None:
        return ApiResponseOUT[T | ErrorData](  # change return type
            status_code=raw_response.status_code,
            url=raw_response.url,
            debug=raw_response.debug,
            meta=raw_response.meta.copy() if raw_response.meta else None,
            parse=CleanAndParseStatus.SKIPPED,
            cleaned_data=ErrorData(
                error_message="No parser model provided", raw_data=raw_response.raw_data
            ),  # wrap data
            description="No parser model provided, raw data forwarded",
        )

    try:
        clean_data = target_model.model_validate(raw_response.raw_data)
        parse_status = CleanAndParseStatus.SUCCESS
        description = "Data berhasil di-parse"
    except ValidationError as e:
        error_data = ErrorData(
            error_message=str(e), raw_data=raw_response.raw_data
        )  # wrap data
        parse_status = CleanAndParseStatus.ERROR
        description = f"Error cleansing data: {e}"

        # log hanya sekali, bind model dan URL biar jelas
        logger.bind(url=raw_response.url, model=target_model.__name__).warning(
            description
        )

        return ApiResponseOUT[T | ErrorData](  # change return type
            status_code=raw_response.status_code,
            url=raw_response.url,
            debug=raw_response.debug,
            meta=raw_response.meta.copy() if raw_response.meta else None,
            parse=parse_status,
            cleaned_data=error_data,
            description=description,
        )

    return ApiResponseOUT[T | ErrorData](  # change return type
        status_code=raw_response.status_code,
        url=raw_response.url,
        debug=raw_response.debug,
        meta=raw_response.meta.copy() if raw_response.meta else None,
        parse=parse_status,
        cleaned_data=clean_data,
        description=description,
    )


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
