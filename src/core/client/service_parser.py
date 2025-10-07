from enum import StrEnum
from typing import Any

import httpx

from utils.log_utils import timeit


class ResponseMessage(StrEnum):
    """Tipe pesan atau struktur data hasil parsing body response."""

    DICT = "DICT"  # Body adalah dictionary
    LIST = "LIST"  # Body adalah list
    TEXT = "TEXT"  # Body adalah string (teks, html, xml, dll.)
    PRIMITIVE = "PRIMITIVE"  # Body adalah tipe data primitif (int, bool, float, dll.)
    EMPTY = "EMPTY"  # Body kosong
    ERROR = "ERROR"  # Terjadi error saat parsing
    UNKNOWN = "UNKNOWN"  # Tipe tidak terdeteksi atau error tidak terduga


@timeit
def _parse_text_safe(resp: httpx.Response) -> tuple[ResponseMessage, dict[str, Any]]:
    """Mencoba parsing body sebagai teks (fallback) dan mendeteksi EMPTY."""
    try:
        text = resp.text.strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
    except Exception as e:
        # Error saat mengakses resp.text (misal: koneksi terputus saat membaca)
        return ResponseMessage.ERROR, {
            "error": f"Text reading failed: {e}",
            "raw": None,
        }

    return ResponseMessage.TEXT, {"raw": text}


@timeit
def _parse_json_safe(
    resp: httpx.Response,
) -> tuple[ResponseMessage, dict[str, Any] | Any]:
    """Mencoba parsing body sebagai JSON, menangani berbagai tipe data JSON."""
    try:
        body = resp.json()
        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            # Mengembalikan list sebagai bagian dari dict untuk konsistensi
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
    except httpx.DecodingError:
        # Gagal decode JSON, coba parsing sebagai teks
        return _parse_text_safe(resp)
    except Exception as e:
        # Error lain saat parsing JSON
        return ResponseMessage.ERROR, {
            "error": f"JSON parsing failed: {e}",
            "raw": getattr(resp, "text", None),
        }

    # Tipe data primitif JSON (string, number, boolean)
    return ResponseMessage.PRIMITIVE, {"raw": body}


@timeit
def _parse_body(resp: httpx.Response) -> tuple[ResponseMessage, dict[str, Any] | Any]:
    """Logika utama untuk mendeteksi content-type dan parsing body."""
    content_type = resp.headers.get("content-type", "").lower()

    # 1. Prioritas utama: JSON
    if "json" in content_type:
        return _parse_json_safe(resp)

    # 2. Prioritas kedua: Teks/HTML/XML/Plain
    if "text" in content_type or "html" in content_type or "xml" in content_type:
        return _parse_text_safe(resp)

    # 3. Default: Coba parse JSON (fallback)
    result_type, result_data = _parse_json_safe(resp)

    # Jika hasil coba-coba JSON parsing adalah ERROR, fallback ke parsing teks biasa.
    if result_type == ResponseMessage.ERROR:
        return _parse_text_safe(resp)

    return result_type, result_data


# --- Metadata Helpers ---


# Core Meta: Selalu diperlukan untuk Service Layer
def _get_core_meta(resp: httpx.Response) -> dict[str, Any]:
    """Ekstrak metadata esensial (status code, url, waktu) untuk logika bisnis."""
    return {
        "url": resp.url.host,
        "path": resp.url.path,
        "status_code": resp.status_code,
        "reason_phrase": resp.reason_phrase,
        "elapsed_time_s": resp.elapsed.total_seconds(),
        "content_type": resp.headers.get("content-type"),
    }


@timeit
def _get_debug_meta(resp: httpx.Response) -> dict[str, Any]:
    """Ekstrak metadata detail (header) hanya untuk debugging."""
    return {
        "method": resp.request.method if resp.request else None,
        "request_headers": dict(resp.request.headers) if resp.request else None,
        "response_headers": dict(resp.headers),
        "response_history": [dict(r.headers) for r in resp.history],
        "response_cookies": dict(resp.cookies),
    }


# --- Main Conversion Function ---


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Mengubah httpx.Response menjadi dictionary standar yang bersih dan terstruktur.

    Args:
        resp: Objek httpx.Response mentah.
        debugresponse: Jika True, akan menyertakan header request/response detail.

    Returns:
        Dict terstruktur dengan kunci 'meta' dan 'data'.
    """
    # 1. SELALU ambil Core Meta
    metadata = _get_core_meta(resp)

    # 2. Ambil Debug Meta HANYA jika diperlukan
    if debugresponse:
        metadata.update(_get_debug_meta(resp))  # Gabungkan ke metadata yang sudah ada

    # 3. Parse body
    body_type, parsed_data = _parse_body(resp)

    # Tambahkan body_type ke metadata agar Service Layer mudah mengaksesnya
    # Tanpa harus mengakses 'body_type' di level root dict
    metadata["body_type"] = body_type

    # 4. Gabungkan menjadi dictionary standar
    return {
        "meta": metadata,
        "data": parsed_data,
    }
