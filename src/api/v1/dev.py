import httpx
from fastapi import APIRouter
from loguru import logger

from src.deps import DepDigiposApiClient, DepDigiposSettings
from src.services.digipos.srv_commands import DigiposCommands

router = APIRouter(prefix="/test", tags=["test"])


@router.get(
    "/get_api",
    summary="just an explore (Reliable Content Check)",
)
async def test_api(
    client: DepDigiposApiClient,
    config: DepDigiposSettings,
):
    """Explores API calls and reliably checks content type."""
    commands = DigiposCommands(config)
    response_obj = await commands.get_balance(client)
    return response_obj.to_ready_dict()


@router.get(
    "/expplore",
    summary="exploring the apis",
)
async def explore_api(
    client: DepDigiposApiClient,
):
    """Explores API Response with httpx library"""
    endpoint = "command"
    params = {"username": "WIR6289504"}
    logger.debug(f"sending request to {endpoint} with params {params}")

    # 1. Panggil API dan Tangani Kegagalan Koneksi/Status
    try:
        raw_response = await client.get(url=endpoint, params=params)
        raw_response.raise_for_status()

        # Sukses Status 2xx - Lanjut ke body, ambil status code sukses
        http_status = raw_response.status_code
        is_success = True

    except httpx.RequestError as exc:
        # Kegagalan Koneksi - Return Dict Gagal
        return {
            "is_success": False,
            "http_status": 0,  # Atau None, menandakan kegagalan jaringan sebelum response
            "payload": {
                "error": "HTTPConnectionError",
                "message": f"HTTP Error: {exc}",
            },
        }
    except httpx.HTTPStatusError as exc:
        # Kegagalan Status Code 4xx/5xx - Return Dict Gagal
        return {
            "is_success": False,
            "http_status": exc.response.status_code,
            "payload": {"error": "HttpResponseError", "message": f"HTTP Error: {exc}"},
        }

    # --- 2. Penanganan Body Respons (Hanya Jika Status 2xx) ---
    final_payload = {}
    try:
        data = raw_response.json()

        # A. Jika data berupa list (Array JSON)
        if isinstance(data, list):
            final_payload = {"items": data, "count": len(data)}

        # B. Jika data berupa primitive (string, int, bool) atau dict
        elif isinstance(data, dict):
            final_payload = data  # Biarkan dict yang valid apa adanya
        else:
            final_payload = {"raw_data": data}  # Bungkus primitive

    except ValueError:
        # C. Jika parsing JSON gagal (meskipun status 2xx)
        is_success = False  # Ubah status sukses menjadi gagal karena body rusak
        final_payload = {"error": "JSONDecodeError", "raw_response": raw_response.text}

    # 3. Return Konsisten (Sukses/JSON Decode Error)
    return {
        "is_success": is_success,
        "http_status": http_status,
        "payload": final_payload,
    }
