"""router testing for developements exploring."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.deps import Depends, ServiceDigipos, get_digipos_service

router = APIRouter(prefix="/test", tags=["test"])


@router.get(
    "/get_api",
    summary="just an explore",
    response_class=PlainTextResponse,
    response_model=str,
)
async def test_api(service: ServiceDigipos = Depends(get_digipos_service)):
    """exploring the api calls and methode."""
    return await service.get_balance()
