# src/core/utils/output_utils.py

import json
from typing import Any, Dict


def _format_value(value: Any) -> str:
    """
    Convert dict/list ke string tanpa tanda kutip berlebihan.
    Tujuan: hasil clean dan regex-friendly.
    """
    if isinstance(value, (dict, list)):
        json_str = json.dumps(value, ensure_ascii=False)
        # hapus kutip dari key & value sederhana
        clean_str = json_str.replace('"', "").replace("'", "")
        return clean_str
    if value is None:
        return "null"
    return str(value)


def encode_response_upstream(response_dict: Dict[str, Any]) -> str:
    """
    Encode dict hasil response_upstream_to_dict jadi string:
    Contoh:
    api_status_code=200&meta={url:http...,method:GET}&data={...}
    """
    parts = []
    for key, value in response_dict.items():
        try:
            parts.append(f"{key}={_format_value(value)}")
        except Exception as e:
            # fallback aman kalau ada value aneh
            parts.append(f"{key}=<encode_error:{e}>")
    return "&".join(parts)
