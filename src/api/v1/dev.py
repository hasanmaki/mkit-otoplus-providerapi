# src/api/v1/dev.py
from fastapi import APIRouter
from loguru import logger

from deps.digipos import DepDigiposApiClient, DepDigiposHttpService, DepDigiposSettings
from src.core.utils.client_utils import handle_response, request_handler

router = APIRouter(prefix="/test", tags=["test"])


@router.get(
    "/expplore",
    summary="inject only Client Service.",
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
async def test(service: DepDigiposHttpService, dgsettings: DepDigiposSettings):
    """Injecting http service only."""
    params = {"username": dgsettings.username}
    result = await service.safe_request("GET", "balance", params=params)
    return result
