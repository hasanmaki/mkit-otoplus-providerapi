from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError

from services.client.response_model import (
    ApiResponseIN,
    ApiResponseOUT,
    CleanAndParseStatus,
)
from utils.log_utils import logger_wraps, timeit

T = TypeVar("T", bound=BaseModel)


@logger_wraps()
@timeit
def clean_validate_raw_dict_data[T: BaseModel](
    raw_response: ApiResponseIN, target_model: type[T] | None = None
) -> ApiResponseOUT[T | Any]:
    """Generic cleaner + parser.

    - raw_response: ApiResponseIN
    - target_model: Optional Pydantic model
    Returns: ApiResponseOUT[T] dengan type-safe cleaned_data
    kalau model lain belum ada model :
    call : clean_validate_raw_dict_data(raw_response)
    """
    if target_model is None:
        return ApiResponseOUT[T | Any](
            status_code=raw_response.status_code,
            url=raw_response.url,
            debug=raw_response.debug,
            meta=raw_response.meta.copy() if raw_response.meta else None,
            parse=CleanAndParseStatus.SKIPPED,
            cleaned_data=raw_response.raw_data,
            description="No parser model provided, raw data forwarded",
        )

    try:
        clean_data = target_model.model_validate(raw_response.raw_data)
        parse_status = CleanAndParseStatus.SUCCESS
        description = "Data berhasil di-parse"
    except ValidationError as e:
        clean_data = raw_response.raw_data
        parse_status = CleanAndParseStatus.ERROR
        description = f"Error cleansing data: {e}"

        # log hanya sekali, bind model dan URL biar jelas
        logger.bind(url=raw_response.url, model=target_model.__name__).warning(
            description
        )

    return ApiResponseOUT[T](
        status_code=raw_response.status_code,
        url=raw_response.url,
        debug=raw_response.debug,
        meta=raw_response.meta.copy() if raw_response.meta else None,
        parse=parse_status,
        cleaned_data=clean_data,
        description=description,
    )


def fallback_response(
    raw_response: ApiResponseIN | None = None, description: str = "No response received"
) -> ApiResponseOUT[Any]:
    """Build a standard SKIPPED response.

    - If raw_response is provided, preserve meta, url, status_code, debug.
    - Otherwise, return default values.
    """
    if raw_response:
        return ApiResponseOUT[Any](
            status_code=raw_response.status_code,
            url=raw_response.url,
            debug=raw_response.debug,
            meta=raw_response.meta.copy() if raw_response.meta else None,
            parse=CleanAndParseStatus.SKIPPED,
            cleaned_data=None or raw_response.raw_data,
            description=description,
        )
    return ApiResponseOUT[Any](
        status_code=0,
        url="",
        debug=False,
        meta=None,
        parse=CleanAndParseStatus.SKIPPED,
        cleaned_data=None,
        description=description,
    )
