# src/api/v1/dev.py
from fastapi import APIRouter
from loguru import logger

from deps.digipos import DepDigiposApiClient, DepDigiposHttpService, DepDigiposSettings
from src.core.utils.client_utils import handle_response, request_handler

router = APIRouter(prefix="/test", tags=["test"])


@router.get(
    "/test_raw",
    summary="testing with raw cleint and service builder.",
)
async def explore_api(
    client: DepDigiposApiClient,
):
    """Testing with raw cleint and service builder."""
    endpoint = "command"
    params = {"username": "WIR6289504"}
    logger.debug(f"sending request to {endpoint} with params {params}")

    try:
        raw_response = await request_handler(client, "GET", endpoint, params=params)
        result = handle_response(raw_response)
    except Exception:
        return {"message": "the app cant things again what kind of response its"}
    return result


@router.get("/test_service")
async def test(service: DepDigiposHttpService, dgsettings: DepDigiposSettings):
    """Testing with injected service."""
    params = {"username": dgsettings.username}
    debug: bool = dgsettings.debug
    endpoint: str = "command"
    result = await service.safe_request(
        "GET", endpoint=endpoint, params=params, debugresponse=debug
    )
    return result
