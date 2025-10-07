from typing import Annotated

from fastapi import APIRouter, Depends, Query

from deps.digipos import (
    DepDigiposCommandService,
)
from schemas.sch_digipos import DGReqUsername, DGReqUsnOtp, DGReqUsnPass

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(
    path="/login",
    summary="Forward login command to Digipos API",
)
async def get_login(
    query: Annotated[DGReqUsnPass, Depends()],
    service: DepDigiposCommandService,
):
    """Get login ke digipos Account API."""
    response_model = await service.login(query)

    return response_model


@router.get(
    path="/verify_otp",
    summary="Forward verify OTP command to Digipos API",
)
async def get_verify_otp(
    query: Annotated[DGReqUsnOtp, Depends()],
    service: DepDigiposCommandService,
):
    """Get verify OTP ke digipos Account API."""
    response_model = await service.verify_otp(query)

    return response_model


@router.get(
    "/balance",
    summary="Forward Balance command to Digipos API",
    response_model=None,
)
async def get_balance(
    query: Annotated[DGReqUsername, Query()],
    service: DepDigiposCommandService,
):
    """Forward `get` balance ke Account Digipos API."""
    response_model = await service.balance(query)
    return response_model


@router.get(
    path="/profile",
    summary="Forward profile command to Digipos API",
)
async def get_profile(
    query: Annotated[DGReqUsername, Depends()],
    service: DepDigiposCommandService,
):
    """Ambil profile dari Digipos API."""
    response_model = await service.profile(query)

    return response_model


@router.get(
    path="/list_va",
    summary="Forward list_va command to Digipos API",
)
async def get_list_va(
    query: Annotated[DGReqUsername, Depends()],
    service: DepDigiposCommandService,
):
    """Ambil list_va dari Digipos API."""
    response_model = await service.list_va(query)

    return response_model


@router.get(
    path="/reward",
    summary="Forward reward command to Digipos API",
)
async def get_reward(
    query: Annotated[DGReqUsername, Depends()],
    service: DepDigiposCommandService,
):
    """Ambil reward dari Digipos API."""
    response_model = await service.reward(query)

    return response_model


@router.get(
    path="/banner",
    summary="Forward banner command to Digipos API",
)
async def get_banner(
    query: Annotated[DGReqUsername, Depends()],
    service: DepDigiposCommandService,
):
    """Ambil banner dari Digipos API."""
    response_model = await service.banner(query)

    return response_model


@router.get(
    path="/logout",
    summary="Forward logout command to Digipos API",
)
async def get_logout(
    query: Annotated[DGReqUsername, Depends()],
    service: DepDigiposCommandService,
):
    """Logout dari Digipos API."""
    response_model = await service.logout(query)

    return response_model


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
