from typing import Annotated

from fastapi import APIRouter, Depends, Query

from deps.digipos import (
    DepDigiposCommandService,
    DepDigiposHttpService,
    DepDigiposSettings,
)
from schemas.sch_digipos import DGReqUsername, DGReqUsnOtp, DGReqUsnPass

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(
    path="/login",
    summary="Forward login command to Digipos API",
)
async def login(
    query: Annotated[DGReqUsnPass, Depends()],
    http_service: DepDigiposHttpService,
    settings: DepDigiposSettings,
):
    """Get login ke digipos Account API."""
    params = {"username": query.username}
    if query.username != settings.username:
        raise ValueError("Username tidak sesuai dengan yang terdaftar")
    if query.password != settings.password:
        raise ValueError("Password tidak sesuai dengan yang terdaftar")
    endpoint = settings.endpoints.login
    debugresponse = settings.debug
    response_model = await http_service.safe_request(
        "GET", endpoint=endpoint, params=params, debugresponse=debugresponse
    )
    return response_model


@router.get(
    path="/verify_otp",
    summary="Forward verify OTP command to Digipos API",
)
async def verify_otp(
    query: Annotated[DGReqUsnOtp, Depends()],
    http_service: DepDigiposHttpService,
    settings: DepDigiposSettings,
):
    """Get verify OTP ke digipos Account API."""
    params = {"username": query.username}
    if query.username != settings.username:
        raise ValueError("Username tidak sesuai dengan yang terdaftar")
    endpoint = settings.endpoints.verify_otp
    debugresponse = settings.debug
    response_model = await http_service.safe_request(
        "GET", endpoint=endpoint, params=params, debugresponse=debugresponse
    )
    return response_model


@router.get(
    "/balance",
    summary="Forward Balance command to Digipos API",
    response_model=None,
)
async def balance(
    query: Annotated[DGReqUsername, Query()],
    service: DepDigiposCommandService,  # Ganti definisi dependensi di sini
):
    """Keterangan: Di sini, FastAPI akan mengenali DepDigiposCommandService.

    sebagai tipe dependensi *tanpa* mengeksposnya sebagai parameter permintaan.
    """
    response_model = await service.balance(query)
    return response_model


@router.get(
    path="/profile",
    summary="Forward profile command to Digipos API",
)
async def profile(
    query: Annotated[DGReqUsername, Depends()],
    http_service: DepDigiposHttpService,
    settings: DepDigiposSettings,
):
    """Ambil profile dari Digipos API."""
    params = {"username": query.username}
    if query.username != settings.username:
        raise ValueError("Username tidak sesuai dengan yang terdaftar")
    endpoint = settings.endpoints.profile
    debugresponse = settings.debug
    response_model = await http_service.safe_request(
        "GET", endpoint=endpoint, params=params, debugresponse=debugresponse
    )
    return response_model


# @router.get(
#     path="/list_va",
#     summary="Forward list_va command to Digipos API",
#     response_class=PlainTextResponse,
# )
# async def list_va(
#     service: ServiceDigiposAccount = Depends(get_digipos_account_service),
# ):
#     """Ambil list_va dari Digipos API."""
#     response_model = await service.list_va()
#     return response_model


# @router.get(
#     path="/rewardsummary",
#     summary="Forward rewardsummary command to Digipos API",
#     response_class=PlainTextResponse,
# )
# async def get_reward(
#     service: ServiceDigiposAccount = Depends(get_digipos_account_service),
# ):
#     """Ambil rewardsummary dari Digipos API."""
#     response_model = await service.reward()
#     return response_model


# @router.get(
#     path="/banner",
#     summary="Forward banner command to Digipos API",
#     response_class=PlainTextResponse,
# )
# async def get_banner(
#     service: ServiceDigiposAccount = Depends(get_digipos_account_service),
# ):
#     """Ambil banner dari Digipos API."""
#     response_model = await service.banner()
#     return response_model


# @router.get(
#     path="/logout",
#     summary="Forward logout command to Digipos API",
#     response_class=PlainTextResponse,
# )
# async def logout(service: ServiceDigiposAccount = Depends(get_digipos_account_service)):
#     """Logout dari Digipos API."""
#     response_model = await service.logout()
#     return response_model


# @router.get(
#     path="/balance",
#     summary="Forward balance command to Digipos API",
#     responses={
#         200: {
#             "content": {
#                 "text/plain": {
#                     "example": "api_status_code=200#meta={'x-powered-by': 'Express', 'content_type': 'application/json; charset=utf-8', 'content_length': '146', 'elapsed_ms': 887.54, 'host': '10.0.0.3', 'path': '/balance', 'method': 'GET'}#data={'ngrs': {'1000': '0', '5000': '0', '10000': '0', '15000': '0', '20000': '0', '25000': '0', '50000': '0', '100000': '0', 'BULK': '0'}, 'linkaja': '3230', 'finpay': '0'}"
#                 }
#             }
#         }
#     },
#     response_class=PlainTextResponse,
# )
# async def balance(
#     service: ServiceDigiposAccount = Depends(get_digipos_account_service),
# ):
#     """Ambil balance dari Digipos API dan return sebagai text-friendly.
#     Format:
#     api_status_code=&meta=&data=
#     """
#     response_model = await service.get_balance()
#     return response_model
