"""Router testing for development / exploration."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.deps import ServiceDigiposAccount, get_digipos_account_service
from src.schemas.base_response import ApiResponse

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(
    "/login",
    summary="Forward login command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def login(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
    """Login ulang ke account Digipos API."""
    response_model = await service.get_login()
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    "/verify_otp",
    summary="Forward verify OTP command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def verify_otp(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service), otp: str = ""
):
    """Verify OTP untuk login ulang ke Digipos API."""
    response_model = await service.get_verify_otp(otp)
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    "/balance",
    summary="Forward balance command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def balance(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil balance dari Digipos API."""
    response_model = await service.get_balance()
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    path="/profile",
    summary="Forward profile command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def profile(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil profile dari Digipos API."""
    response_model = await service.get_profile()
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    path="/list_va",
    summary="Forward list_va command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def list_va(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil list_va dari Digipos API."""
    response_model = await service.get_list_va()
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    path="/rewardsummary",
    summary="Forward rewardsummary command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def get_reward(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil rewardsummary dari Digipos API."""
    response_model = await service.get_rewardsummary()
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    path="/banner",
    summary="Forward banner command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def get_banner(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil banner dari Digipos API."""
    response_model = await service.get_banner()
    return PlainTextResponse(content=response_model.model_dump_json())


@router.get(
    path="/logout",
    summary="Forward logout command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def logout(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
    """Logout dari Digipos API."""
    response_model = await service.get_logout()
    return PlainTextResponse(content=response_model.model_dump_json())
