from enum import StrEnum
from typing import Any

import httpx


class ResponseMessage(StrEnum):
    """Tipe pesan atau struktur data hasil parsing body response."""

    DICT = "DICT"  # Body adalah dictionary
    LIST = "LIST"  # Body adalah list
    TEXT = "TEXT"  # Body adalah string (teks, html, xml, dll.)
    PRIMITIVE = "PRIMITIVE"  # Body adalah tipe data primitif (int, bool, float, dll.)
    EMPTY = "EMPTY"  # Body kosong
    ERROR = "ERROR"  # Terjadi error saat parsing
    UNKNOWN = "UNKNOWN"  # Tipe tidak terdeteksi atau error tidak terduga


def _parse_json_safe(
    resp: httpx.Response,
) -> tuple[ResponseMessage, dict[str, Any] | Any]:
    """Mencoba parsing body sebagai JSON, menangani berbagai tipe data JSON."""
    try:
        body = resp.json()
        if isinstance(body, dict):
            return ResponseMessage.DICT, body
        if isinstance(body, list):
            # Mengembalikan list sebagai bagian dari dict untuk konsistensi struktur
            return ResponseMessage.LIST, {"items": body, "count": len(body)}
    except httpx.DecodingError:
        # Gagal decode JSON, coba parsing sebagai teks
        return _parse_text_safe(resp)
    except Exception as e:
        # Error lain saat parsing JSON
        return ResponseMessage.ERROR, {
            "error": f"JSON parsing failed: {e}",
            "raw": resp.text,
        }
    return ResponseMessage.PRIMITIVE, {"raw": body}


def _parse_text_safe(resp: httpx.Response) -> tuple[ResponseMessage, dict[str, Any]]:
    """Mencoba parsing body sebagai teks (fallback)."""
    try:
        text = resp.text.strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
    except Exception as e:
        # Error saat mengakses resp.text
        return ResponseMessage.ERROR, {
            "error": f"Text reading failed: {e}",
            "raw": None,
        }

    return ResponseMessage.TEXT, {"raw": text}


def _parse_body(resp: httpx.Response) -> tuple[ResponseMessage, dict[str, Any] | Any]:
    """Logika utama untuk mendeteksi content-type dan parsing body."""
    content_type = resp.headers.get("content-type", "").lower()

    # 1. Prioritas utama: JSON
    if "json" in content_type:
        return _parse_json_safe(resp)

    # 2. Prioritas kedua: Teks/HTML/XML/Plain
    if "text" in content_type or "html" in content_type or "xml" in content_type:
        # Jika bukan JSON, kita anggap sebagai teks
        return _parse_text_safe(resp)

    # 3. Default: Coba parse JSON (terkadang API tidak set content-type dengan benar)
    # Jika gagal, akan fallback ke _parse_text_safe di dalam _parse_json_safe
    result_type, result_data = _parse_json_safe(resp)

    # Jika hasil dari coba-coba JSON parsing adalah ERROR, fallback ke parsing teks biasa.
    if result_type == ResponseMessage.ERROR:
        return _parse_text_safe(resp)

    return result_type, result_data


# --- Helper Function for Metadata ---


def _get_meta(resp: httpx.Response) -> dict[str, Any]:
    """Ekstrak metadata penting dari httpx.Response."""
    return {
        "url": str(resp.url),
        "method": resp.request.method if resp.request else None,
        "status_code": resp.status_code,
        "reason_phrase": resp.reason_phrase,
        "request_headers": dict(resp.request.headers) if resp.request else None,
        "response_headers": dict(resp.headers),
        "content_type": resp.headers.get("content-type"),
        "elapsed_time_s": resp.elapsed.total_seconds(),
        # Anda bisa tambahkan detail lain seperti cookies, history, dll.
    }


# --- Main Conversion Function ---


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Mengubah httpx.Response menjadi dictionary standar yang bersih dan terstruktur.

    Struktur hasil:
    {
        "meta": {...},      # Metadata response (status, url, headers, dll.)
        "body_type": "...", # Tipe body yang terdeteksi (DICT, LIST, TEXT, dll.)
        "data": {...}       # Body yang sudah di-parse dan distandarisasi
    }
    """
    metadata = {}
    if debugresponse:
        metadata = _get_meta(resp)

    # 2. Parse body
    body_type, parsed_data = _parse_body(resp)

    # 3. Gabungkan menjadi dictionary standar
    return {
        "meta": metadata,
        "body_type": body_type,
        "data": parsed_data,
    }
