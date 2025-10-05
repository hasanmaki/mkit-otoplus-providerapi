"""router testing for developements exploring."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.deps import Depends, ServiceDigiposAccount, get_digipos_account_service

router = APIRouter(prefix="/test", tags=["test"])


@router.get(
    "/get_api",
    summary="just an explore",
    response_class=PlainTextResponse,
)
async def test_api(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """exploring the api calls and methode."""
    response_model = await service.get_balance()
    return PlainTextResponse(content=response_model.model_dump_json())
