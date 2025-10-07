from dataclasses import asdict, dataclass
from typing import Any

from src.config.constant import ResponseMessage


@dataclass
class NormalizedResponse:
    status_code: int
    url: str
    meta: dict[str, Any]
    message: str
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    # ----------------------------------------------------------
    # Factory helpers
    # ----------------------------------------------------------

    @classmethod
    def ok(
        cls,
        resp: Any,
        *,
        message: str,
        data: dict[str, Any],
        meta: dict[str, Any] | None = None,
    ) -> "NormalizedResponse":
        """Response normal (berhasil)."""
        return cls(
            status_code=getattr(resp, "status_code", 200),
            url=str(getattr(getattr(resp, "request", None), "url", "")),
            meta=meta or {},
            message=message,
            data=data,
        )

    @classmethod
    def error(
        cls,
        url: str,
        *,
        error: Exception,
        message: str = ResponseMessage.INTERNAL_ERROR,
    ) -> "NormalizedResponse":
        """Response gagal (error)."""
        return cls(
            status_code=0,
            url=url,
            meta={},
            message=message,
            data={"error": str(error)},
        )
