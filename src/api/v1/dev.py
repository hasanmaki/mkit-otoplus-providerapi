# src/api/v1/dev.py
from fastapi import APIRouter
from loguru import logger

from src.core.client.main_service import HttpClientService
from src.core.utils.client_utils import handle_response, request_handler
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
    """Explores API Response with httpx library."""
    endpoint = "command"
    params = {"username": "WIR6289504"}
    logger.debug(f"sending request to {endpoint} with params {params}")

    try:
        raw_response = await request_handler(client, "GET", endpoint, params=params)
        result = handle_response(raw_response)
    except Exception:
        return {"message": "the app cant things again what kind of response its"}
    return result


@router.get("/test_digipos")
async def test(client: DepDigiposApiClient):
    service = HttpClientService(client)
    result = await service.safe_request(
        "GET", "balance", params={"username": "WIR6289504"}
    )
    return result
