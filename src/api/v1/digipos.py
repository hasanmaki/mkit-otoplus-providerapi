"""Router testing for development / exploration."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.deps import ServiceDigipos, get_digipos_service

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(
    "/login",
    summary="Forward login command to Digipos API",
    response_class=PlainTextResponse,
)
async def login(service: ServiceDigipos = Depends(get_digipos_service)):
    """Login ulang ke account Digipos API."""
    response_model = await service.get_login()
    return PlainTextResponse(content=response_model.json())


@router.get(
    "/verify_otp",
    summary="Forward verify OTP command to Digipos API",
    response_class=PlainTextResponse,
)
async def verify_otp(
    service: ServiceDigipos = Depends(get_digipos_service), otp: str = ""
):
    """Verify OTP untuk login ulang ke Digipos API."""
    response_model = await service.get_verify_otp(otp)
    return PlainTextResponse(content=response_model.json())


@router.get(
    "/balance",
    summary="Forward balance command to Digipos API",
    response_class=PlainTextResponse,
)
async def balance(service: ServiceDigipos = Depends(get_digipos_service)):
    """Ambil balance dari Digipos API."""
    response_model = await service.get_balance()
    return PlainTextResponse(content=response_model.json())
