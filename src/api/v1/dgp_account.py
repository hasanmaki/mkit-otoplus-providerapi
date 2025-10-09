from typing import Annotated

from fastapi import APIRouter, Depends, Query

from deps.dep_digipos import (
    DepDigiposCommandService,
)
from servicess.client.depre_cated_response_model import ApiResponseOUT
from servicess.digipos.sch_digipos import (
    DGReqSimStatus,
    DGReqUsername,
    DGReqUsnOtp,
    DGReqUsnPass,
    DGResBalance,
)
from servicess.parser.parser_utils import ApiErrorParsing, dict_to_plaintext
from src.tag import Tags as Tag

router = APIRouter(
    prefix="/digipos",
)


@router.get(
    path="/login",
    summary="Forward login command to Digipos API",
    tags=[Tag.digipos_account],
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
    tags=[Tag.digipos_account],
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
    response_model=ApiResponseOUT[DGResBalance | ApiErrorParsing] | str,
    tags=[Tag.digipos_account],
)
async def get_balance(
    query: Annotated[
        DGReqUsername, Query()
    ],  # Anggap query sekarang punya field 'text'
    service: DepDigiposCommandService,
):
    """Forward `get` balance ke Account Digipos API.

    Kontrol output: data murni (tanpa metadata) jika query.text=True.
    """
    response_model = await service.balance(query)

    text_source = response_model.model_dump()
    text_response = dict_to_plaintext(text_source)

    # 2. Kontrol output API berdasarkan parameter 'text'
    if query.text:
        return text_response

    return response_model


@router.get(
    path="/profile",
    summary="Forward profile command to Digipos API",
    tags=[Tag.digipos_account],
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
    tags=[Tag.digipos_account],
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
    tags=[Tag.digipos_account],
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
    tags=[Tag.digipos_account],
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
    tags=[Tag.digipos_account],
)
async def get_logout(
    query: Annotated[DGReqUsername, Depends()],
    service: DepDigiposCommandService,
):
    """Logout dari Digipos API."""
    response_model = await service.logout(query)

    return response_model


@router.get(
    path="/sim_status",
    summary="Forward sim_status command to Digipos API",
    tags=[Tag.digipos_utils],
)
async def get_sim_status(
    query: Annotated[DGReqSimStatus, Depends()],
    service: DepDigiposCommandService,
):
    """Ambil sim_status dari Digipos API."""
    response_model = await service.sim_status(query)

    return response_model
