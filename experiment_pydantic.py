from collections.abc import MutableMapping
from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T")
PayloadModel = TypeVar("PayloadModel", bound=BaseModel)


class ParsedStatus(StrEnum):
    OK = "OK"
    ERROR = "ERROR"
    FORWARD = "FORWARD"


class ApiRawResponse(BaseModel):
    status_code: int
    url: str
    meta: dict[str, Any]
    message: str
    data: dict[str, Any]


class DGResBalance(BaseModel):
    ngrs: dict[str, str]
    linkaja: str
    finpay: str


class ApiResponseProcessor(BaseModel, Generic[T]):
    status_code: int
    url: str
    meta: dict[str, Any]
    parsed: ParsedStatus
    data: T


class ApiSuccessParseResponse(ApiResponseProcessor[DGResBalance]):
    """Digunakan saat parsing sukses (parsed=OK). Data = DGResBalance."""

    parsed: ParsedStatus = ParsedStatus.OK  # Set default agar jelas


class ApiFailedParseResponse(ApiResponseProcessor[dict[str, Any]]):
    """Digunakan saat parsing gagal/forward (parsed=FORWARD/ERROR). Data = dict[str, Any]."""


# =====================================================================
# 3. UTILITY FUNCTIONS
# =====================================================================


def convert_to_plaintext_final(data: dict[str, Any]) -> str:
    """Mengubah dictionary menjadi string plaintext kustom.

    - Menghapus 'message'.
    - Membungkus 'url' dengan tanda kurung () tanpa encoding.
    - Data dan Meta menggunakan representasi string Python (str()).
    """
    final_parts = []
    for key, value in data.items():
        if key == "message":
            continue  # Hapus kunci message

        processed_value = str(value)

        if key == "url":
            # Membungkus URL dengan tanda kurung ()
            processed_value = f"({value})"

        elif key in ("data", "meta") and isinstance(value, MutableMapping):
            # Data dan Meta menggunakan representasi string Python
            processed_value = str(value)

        # Kunci lain (status_code, parsed) dibiarkan mentah
        final_parts.append(f"{key}={processed_value}")

    return "&".join(final_parts)


def try_parse_payload(
    data: dict[str, Any], payload_model: type[PayloadModel]
) -> tuple[bool, PayloadModel | dict[str, Any]]:
    """Mencoba memvalidasi data terhadap model Pydantic yang diberikan.
    Mengembalikan (status_sukses, data_tervalidasi atau data_mentah).
    """
    try:
        validated_data = payload_model(**data)
        return True, validated_data
    except ValidationError:
        return False, data  # Kembalikan data mentah jika gagal validasi


def process_response_generic(
    raw_response_dict: dict[str, Any],
    target_payload_model: type[PayloadModel] | None = None,
) -> str:
    """Memproses response mentah (dict) secara generik.

    Args:
        raw_response_dict: Dictionary respons yang sudah dinormalisasi (ApiRawResponse structure).
        target_payload_model: Model Pydantic spesifik (misal DGResBalance) untuk divalidasi
                              jika message-nya 'DICT'. Jika None, tidak ada validasi spesifik.
    """
    # JALUR 1: Validasi Model Raw (Memastikan struktur level atas benar)
    try:
        raw_data = ApiRawResponse(**raw_response_dict)
    except ValidationError:
        # Jika struktur level atas gagal, anggap ini error fatal/ERROR
        error_dict = {
            # ... (Logika error fatal TETAP SAMA) ...
            "status_code": raw_response_dict.get("status_code", 500),
            "url": raw_response_dict.get("url", "validation_failed"),
            "meta": {},
            "parsed": ParsedStatus.ERROR.value,
            "data": "Raw structure validation failed",
            "message": "INTERNAL_VALIDATION_FAIL",
        }
        return convert_to_plaintext_final(error_dict)

    # JALUR 2: Logika Parsing Spesifik
    output_model_instance = None
    should_validate = raw_data.message == "DICT" and target_payload_model is not None

    if not should_validate:
        # KASUS A: message != DICT, ATAU target_payload_model tidak diberikan -> FORWARD
        parsed_status = ParsedStatus.FORWARD
        if raw_data.message == "DICT" and target_payload_model is None:
            print(
                "[LOG] Message is DICT but no specific model was provided. Forwarding."
            )
        else:
            print(f"[LOG] Message is '{raw_data.message}'. Forwarding raw data.")

        output_model_instance = ApiFailedParseResponse(
            **raw_data.model_dump(), parsed=parsed_status
        )
    else:
        # KASUS B: message == DICT DAN ada target_payload_model -> Validasi

        # Gunakan helper baru yang generik
        is_success, result_data = try_parse_payload(raw_data.data, target_payload_model)

        if is_success:
            # KASUS B.1: Data valid -> OK
            print("[LOG] Message is DICT and data is valid. Status: OK.")

            # Kita harus menggunakan ApiResponseProcessor generik di sini karena kita tidak tahu tipe spesifiknya
            # di luar fungsi ini. Atau kita hanya perlu mengasumsikan tipe data kembali ke dict[str, Any]
            # dan biarkan API client yang menentukan tipe data yang benar.

            output_model_instance = ApiSuccessParseResponse(
                status_code=raw_data.status_code,
                url=raw_data.url,
                meta=raw_data.meta,
                data=result_data,  # Data yang sudah tervalidasi (tipe PayloadModel)
                message=raw_data.message,
            )
        else:
            # KASUS B.2: Data tidak valid -> FORWARD (Data mentah digunakan)
            print("[LOG] Message is DICT but data is INVALID. Forwarding raw data.")
            output_model_instance = ApiFailedParseResponse(
                **raw_data.model_dump(), parsed=ParsedStatus.FORWARD
            )

    # JALUR 3: Final Encoding
    return convert_to_plaintext_final(output_model_instance.model_dump())


# =====================================================================
# 5. EXECUTION & TEST CASES
# =====================================================================


def main():
    # --- Test Case 1: SUCCESS (OK) ---
    dict_response_ok = {
        "status_code": 200,
        "url": "http://10.0.0.3:10003/balance",
        "meta": {"trace_id": "xyz123"},
        "message": "DICT",
        "data": {"ngrs": {"1000": "0", "BULK": "0"}, "linkaja": "3230", "finpay": "0"},
    }
    print("--- TEST CASE 1: SUCCESS (OK) ---")
    result_ok = process_response_generic(dict_response_ok)
    print(f"OUTPUT: {result_ok}\n")
    # Expected: parsed=OK

    # --- Test Case 2: INVALID DATA -> FORWARD ---
    dict_response_invalid = dict_response_ok.copy()
    # Menjadikan 'linkaja' integer (seharusnya string)
    dict_response_invalid["data"] = {
        "ngrs": {"1000": "0"},
        "linkaja": 3230,
        "finpay": "0",
    }
    print("--- TEST CASE 2: INVALID DATA -> FORWARD ---")
    result_invalid = process_response_generic(dict_response_invalid)
    print(f"OUTPUT: {result_invalid}\n")
    # Expected: parsed=FORWARD, data tetap berisi integer mentah

    # --- Test Case 3: MESSAGE NON-DICT -> FORWARD ---
    dict_response_non_dict = dict_response_ok.copy()
    dict_response_non_dict["message"] = "PLAIN_TEXT"
    dict_response_non_dict["data"] = {"raw_text": "balance is not available"}
    print("--- TEST CASE 3: MESSAGE NON-DICT -> FORWARD ---")
    result_non_dict = process_response_generic(dict_response_non_dict)
    print(f"OUTPUT: {result_non_dict}\n")
    # Expected: parsed=FORWARD, data tetap berisi payload mentah


if __name__ == "__main__":
    main()
