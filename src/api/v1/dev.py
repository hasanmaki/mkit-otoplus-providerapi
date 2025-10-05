"""router testing for developements exploring."""

import json

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.deps import Depends, ServiceDigipos, get_digipos_service

router = APIRouter(prefix="/test", tags=["test"])


@router.get(
    "/get_api",
    summary="just an explore",
    response_class=PlainTextResponse,
)
async def test_api(service: ServiceDigipos = Depends(get_digipos_service)):
    """exploring the api calls and methode."""

    response_data: dict = await service.get_balance()

    # 1. Serialisasi Dict menjadi string JSON
    json_string = json.dumps(response_data)

    # 2. Bungkus string dalam PlainTextResponse
    return PlainTextResponse(content=json_string)
