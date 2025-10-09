from pydantic import BaseModel, ConfigDict
from typing_extensions import TypeVar

T = TypeVar("T", bound=BaseModel)


class ApiBaseResponse[T](BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )
    url: str
    path: str
    data: T


class ApiErrorResponse(ApiBaseResponse):
    data: str | dict[str, str] | list[str] | None = None


class ApiSuccessResponse[T](ApiBaseResponse[T]): ...
