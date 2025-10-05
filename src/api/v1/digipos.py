"""Router testing for development / exploration."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.deps import ServiceDigiposAccount, get_digipos_account_service

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(
    "/login",
    summary="Forward login command to Digipos API",
)
async def login(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
    response_model = await service.login()
    return response_model


@router.get(
    "/verify_otp",
    summary="Forward verify OTP command to Digipos API",
)
async def verify_otp(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service), otp: str = ""
):
    """Verify OTP untuk login ulang ke Digipos API."""
    response_model = await service.verify_otp(otp)
    return response_model


@router.get(
    path="/balance",
    summary="Forward balance command to Digipos API",
    responses={
        200: {
            "content": {
                "text/plain": {
                    "example": "api_status_code=200#meta={'x-powered-by': 'Express', 'content_type': 'application/json; charset=utf-8', 'content_length': '146', 'elapsed_ms': 887.54, 'host': '10.0.0.3', 'path': '/balance', 'method': 'GET'}#data={'ngrs': {'1000': '0', '5000': '0', '10000': '0', '15000': '0', '20000': '0', '25000': '0', '50000': '0', '100000': '0', 'BULK': '0'}, 'linkaja': '3230', 'finpay': '0'}"
                }
            }
        }
    },
    response_class=PlainTextResponse,
)
async def balance(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """
    Ambil balance dari Digipos API dan return sebagai text-friendly.
    Format:
    api_status_code=&meta=&data=
    """
    response_model = await service.get_balance()
    return response_model


@router.get(
    path="/profile",
    summary="Forward profile command to Digipos API",
)
async def profile(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil profile dari Digipos API."""
    response_model = await service.get_profile()
    return response_model


@router.get(
    path="/list_va",
    summary="Forward list_va command to Digipos API",
    response_class=PlainTextResponse,
)
async def list_va(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil list_va dari Digipos API."""
    response_model = await service.list_va()
    return response_model


@router.get(
    path="/rewardsummary",
    summary="Forward rewardsummary command to Digipos API",
    response_class=PlainTextResponse,
)
async def get_reward(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil rewardsummary dari Digipos API."""
    response_model = await service.reward()
    return response_model


@router.get(
    path="/banner",
    summary="Forward banner command to Digipos API",
    response_class=PlainTextResponse,
)
async def get_banner(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil banner dari Digipos API."""
    response_model = await service.banner()
    return response_model


@router.get(
    path="/logout",
    summary="Forward logout command to Digipos API",
    response_class=PlainTextResponse,
)
async def logout(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
    """Logout dari Digipos API."""
    response_model = await service.logout()
    return response_model
