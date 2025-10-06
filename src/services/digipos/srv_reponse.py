# File: src/services/digipos/digipos_response.py

import json
from typing import Any, Dict

import httpx
from loguru import logger

from src.custom.exceptions import HttpResponseError


class DigiposResponse:
    """
    Kapsulasi httpx.Response, bertugas memastikan:
    1. Response HTTP OK (via raise_for_status).
    2. Parsing konten yang andal (JSON atau Text).
    3. Mengembalikan Dict yang siap di-trim oleh Service Layer.
    """

    def __init__(self, response: httpx.Response):
        self._response = response
        self._log = logger.bind(
            client_url=str(response.request.url), http_status=response.status_code
        )

    def _parse_content(self) -> Dict[str, Any]:
        """
        Melakukan parsing konten body yang andal (JSON decode error handling)
        dan membungkusnya.
        """
        content_type = "JSON"

        try:
            # 1. Selalu coba parsing JSON
            data = self._response.json()

            # 2. Jika JSON sukses tapi bukan dict/list (e.g., string mentah yang di-JSON-kan)
            if not isinstance(data, (dict, list)):
                data = {"raw_data": data}  # Bungkus data non-dict/list

        except json.JSONDecodeError:
            # 3. Fallback: Jika gagal parse JSON, bungkus sebagai teks mentah
            content_type = "Text/Other"
            data = {"raw_text_content": self._response.text}

        # Output dasar yang seragam
        return {
            "http_status_code": self._response.status_code,
            "content_source": content_type,
            "raw_payload": data,
        }

    def to_ready_dict(self) -> Dict[str, Any]:
        """
        Method utama: Memastikan status respons OK, memproses konten, dan
        mengembalikan Dict yang siap diproses/trimming.
        """

        # 1. Pastikan Status OK (Handling 4xx/5xx)
        try:
            self._response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self._log.error(f"Response Status Error: {exc.response.status_code}")
            # Raise Custom Exception untuk 4xx/5xx
            raise HttpResponseError(
                message=f"External service responded with status {exc.response.status_code}",
                context={
                    "url": str(exc.request.url),
                    "response_text": exc.response.text,
                },
                cause=exc,
            ) from exc

        # 2. Parsing dan Standarisasi Output
        parsed_data = self._parse_content()

        # 3. Validasi Isi Body (Empty Check)
        # Kita cek setelah parsing karena mungkin respons 200/204 valid tanpa body.
        data_payload = parsed_data["raw_payload"]
        if data_payload in (None, "", {}, []):
            self._log.warning("Empty response body after parsing.")
            raise HttpResponseError(
                message="Provider returned empty response body",
                context={
                    "status_code": self._response.status_code,
                    "url": str(self._response.request.url),
                    "raw": self._response.text,
                },
            )

        return parsed_data
