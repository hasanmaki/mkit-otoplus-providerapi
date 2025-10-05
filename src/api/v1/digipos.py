"""Router testing for development / exploration."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.deps import ServiceDigiposAccount, get_digipos_account_service
from src.schemas.base_response import ApiResponse
from src.schemas.sch_digipos import ResponseBalance

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(
    "/login",
    summary="Forward login command to Digipos API",
)
async def login(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
    """Login ulang ke account Digipos API."""
    result = await service.get_login()
    if isinstance(result, str):
        # 1. KASUS LEGACY STRING (response_type == 'text')

        # Kembalikan sebagai PlainTextResponse dan tentukan Content-Type-nya
        # agar sesuai dengan format URL-encoded yang diminta klien legacy.
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )

    else:
        # 2. KASUS JSON (response_type != 'text')

        # FastAPI akan secara otomatis men-serialize Model Pydantic ke JSON
        # ResponseBalance atau ApiResponse (fallback) di sini.
        return result


@router.get(
    "/verify_otp",
    summary="Forward verify OTP command to Digipos API",
)
async def verify_otp(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service), otp: str = ""
):
    """Verify OTP untuk login ulang ke Digipos API."""
    result = await service.get_verify_otp(otp)
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result


@router.get(
    path="/balance",
    summary="Forward balance command to Digipos API",
    response_model=ResponseBalance,
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
    result = await service.get_balance()
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result


@router.get(
    path="/profile",
    summary="Forward profile command to Digipos API",
    response_model=ApiResponse,
)
async def profile(
    service: ServiceDigiposAccount = Depends(get_digipos_account_service),
):
    """Ambil profile dari Digipos API."""
    result = await service.get_profile()
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result


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
    result = await service.get_list_va()
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result


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
    result = await service.get_rewardsummary()
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result


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
    result = await service.get_banner()
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result


@router.get(
    path="/logout",
    summary="Forward logout command to Digipos API",
    response_model=ApiResponse,
    response_class=PlainTextResponse,
)
async def logout(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
    """Logout dari Digipos API."""
    result = await service.get_logout()
    if isinstance(result, str):
        return PlainTextResponse(
            content=result, media_type="application/x-www-form-urlencoded"
        )
    else:
        return result
