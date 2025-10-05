import json
from collections.abc import Mapping
from typing import Any, Dict
from urllib.parse import urlencode


def _flatten_dict(dictionary: Dict[Any, Any], parent_key: str = "") -> Dict[str, Any]:
    """
    Recursively flattens a nested dictionary.
    Keys are joined by an underscore (e.g., {'ngrs': {'1000': '0'}} -> {'ngrs_1000': '0'}).
    """
    items = []
    for k, v in dictionary.items():
        new_key = parent_key + str(k) if parent_key else str(k)

        # Check if the value is a dictionary (but not a Pydantic object being dumped)
        if isinstance(v, Mapping):
            items.extend(_flatten_dict(v, new_key + "_").items())
        # Handling lists/tuples (optional, but robust)
        elif isinstance(v, (list, tuple)):
            for i, item in enumerate(v):
                items.append((f"{new_key}_{i}", item))
        else:
            items.append((new_key, v))

    return dict(items)


# --- Output Serialization Functions ---


def model_to_text(model: Any) -> str:
    """
    Serialize Pydantic model ke text-friendly format untuk logging.
    Menggunakan JSON untuk meta dan data agar string lebih bersih.
    """
    fields = model.model_dump()

    # Konversi dict di 'meta' dan 'data' menjadi string JSON yang padat
    meta_json = json.dumps(fields.get("meta", {}), separators=(",", ":"))
    data_json = json.dumps(fields.get("data", {}), separators=(",", ":"))

    return (
        f"api_status_code={fields.get('api_status_code', '')}#"
        f"meta={meta_json}#"
        f"data={data_json}"
    )


def model_to_legacy_string(model: Any) -> str:
    """
    Mengubah Pydantic Model internal menjadi string format URL-encoded (legacy).
    Hanya menggunakan konten dari 'data' dan meratakannya.
    """

    # 1. Dump Pydantic Model ke Dict
    fields = model.model_dump()

    # 2. Ambil data payload dari key 'data'
    data_payload = fields.get("data", {})

    final_data_to_encode: Dict[str, Any] = {}

    # 3. Proses dan Ratakan Data
    if isinstance(data_payload, dict):
        # Data inti diratakan menggunakan helper
        final_data_to_encode = _flatten_dict(data_payload)

    elif isinstance(data_payload, str) and data_payload:
        # Jika data adalah string mentah (fallback parsing), bungkus
        final_data_to_encode["raw_response"] = data_payload

    # 4. Serialisasi ke URL-encoded string
    # urlencode secara otomatis membuat format key1=value1&key2=value2
    return urlencode(final_data_to_encode)
