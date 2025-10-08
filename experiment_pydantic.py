import json
from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel, Field, ValidationError

T = TypeVar("T")


class ParsedStatus(StrEnum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    UNPROCESSED = "UNPROCESSED"


class ApiResponseParser[T](BaseModel):
    """Model Parser Generic — satu kelas untuk semua."""

    meta: dict[str, Any] = Field(default_factory=dict)
    data: Any = Field(default=None)
    parsed: ParsedStatus = ParsedStatus.UNPROCESSED
    message: Any = None
    model: type[BaseModel] | None = None

    @classmethod
    def from_raw(
        cls,
        raw: dict[str, Any],
        model: type[T],
    ):
        """Factory method buat parsing data mentah."""
        meta = raw.get("meta", {})
        data = raw.get("data")

        try:
            parsed_data = model.model_validate(data)  # type: ignore
            return cls(
                meta=meta,
                data=data,
                parsed=ParsedStatus.SUCCESS,
                message=parsed_data.model_dump(),
                model=model,
            )
        except ValidationError as e:
            return cls(
                meta=meta,
                data=data,
                parsed=ParsedStatus.ERROR,
                message={"error": str(e), "raw": data},
                model=model,
            )

    def to_output(self, debug: bool = False) -> str:
        """Output final:
        - debug=True  -> JSON rapi
        - debug=False -> plain key=value&... format
        """
        dump = self.model_dump()

        # ubah 'model' biar bisa di-serialize
        if isinstance(self.model, type):
            dump["model"] = self.model.__name__
        else:
            dump["model"] = str(self.model)

        if debug:
            # mode debug → tampilkan JSON lengkap
            return json.dumps(dump, indent=2, ensure_ascii=False)

        # mode normal → plaintext compact
        meta = dump.get("meta", {})
        parsed = dump.get("parsed", "")
        message = dump.get("message", "")

        url = meta.get("host", "")
        path = meta.get("path", "")
        status = meta.get("status_code", "")

        # normalisasi message
        if isinstance(message, (dict, list)):
            message_str = json.dumps(message, ensure_ascii=False)
        else:
            message_str = str(message)

        # build output string
        str_output = f"url={url}&path={path}&status_code={status}&parsed={parsed}&message={message_str}"
        # hapus semua tanda petik dan spasi yg berlebih
        return str_output.replace('"', "").replace("'", "").replace(" ", "")


# === SAMPLE STRUCT ===
class BalanceData(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


# === SIMULASI RAW DATA ===
raw_success = {
    "meta": {
        "url": "http://10.0.0.3:10003/balance?username=WIR6289504&debug=true",
        "host": "10.0.0.3",
        "path": "/balance",
        "status_code": 200,
        "reason_phrase": "OK",
        "body_type": "DICT",
    },
    "data": {
        "ngrs": {
            "1000": "0",
            "5000": "0",
            "10000": "0",
            "15000": "0",
            "20000": "0",
            "25000": "0",
            "50000": "0",
            "100000": "0",
            "BULK": "0",
        },
        "linkaja": "3230",
        "finpay": "0",
    },
}

raw_failed = {
    "meta": {
        "url": "http://10.0.0.3:10003/balance?username=WIR6289504&debug=true",
        "host": "10.0.0.3",
        "path": "/balance",
        "status_code": 200,
        "reason_phrase": "OK",
        "body_type": "DICT",
    },
    "data": {
        "ngrs": {
            "1000": "0",
            "5000": "0",
            "10000": "0",
            "15000": "0",
            "20000": "0",
            "25000": "0",
            "50000": "0",
            "100000": "0",
            "BULK": "0",
        },
        # missing 'linkaja'
        "finpay": "0",
    },
}

# === TEST ===
parser_ok = ApiResponseParser.from_raw(raw_success, BalanceData)
parser_fail = ApiResponseParser.from_raw(raw_failed, BalanceData)

print("=== NORMAL MODE ===")
print(parser_ok.to_output())
print(parser_fail.to_output())

print("\n=== DEBUG MODE ===")
print(parser_ok.to_output(debug=True))
print(parser_fail.to_output(debug=True))
