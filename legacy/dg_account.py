# TODO: Rapihkan Documnetasi dan buat example response nya di schemas masing masing
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from log_utils import timeit
from src.deps import get_dgaccount_service
from src.domain.digipos.schemas import (
    DGBalanceResponse,
    DGProfileResponse,
    DGReqLogin,
    DGVaResponse,
    DgVerifyOtp,
    DGWithUserName,
)
from src.domain.digipos.services.account_service import DGAccountServices
from src.exception import HTTPGenericError

router = APIRouter(
    prefix="/v1/digipos",
    tags=["digipos"],
)


@router.get(
    path="/login",
    description="Endpoint untuk login ke Digipos",
)
@timeit
async def login(
    request: Annotated[DGReqLogin, Query()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `Login API Digipos`. Jika Addon API Logout, Bisa Login dari Sini."""
    return await account_service.login(request)


@router.get("/verify_otp")
@timeit
async def verify_otp(
    request: Annotated[DgVerifyOtp, Query()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `Verify OTP API Digipos`."""
    return await account_service.verify_otp(request)


@router.get(
    path="/balance",
    response_model=DGBalanceResponse,
    summary="Melihat Saldo Digipos",
)
@timeit
async def balance(
    request: Annotated[DGWithUserName, Query()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """**Melihat Saldo Digipos**.

    - Mendapatkan saldo NGRS, LinkAja, dan Finpay.
    """
    response = await account_service.balance(request)
    return DGBalanceResponse.model_validate(response)


@router.get("/logout")
@timeit
async def logout(
    request: Annotated[DGWithUserName, Depends()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `Logout API Digipos`."""
    return await account_service.logout(request)


@router.get(
    path="/profile",
    summary="Melihat Profile Digipos",
    description="Endpoint untuk melihat profile Digipos: tidak ada normalisasi pydantic schemas karena response dari profile terlalu raw.",
    response_model=DGProfileResponse,
)
@timeit
async def profile(
    request: Annotated[DGWithUserName, Depends()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `Profile API Digipos`."""
    return await account_service.profile(request)


@router.get(
    "/list_va",
    response_model=DGVaResponse,
    summary="Melihat Daftar Virtual Account Digipos",
)
@timeit
async def list_va(
    request: Annotated[DGWithUserName, Depends()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `List VA API Digipos` bisa di gunakan untuk generate tiket."""
    return await account_service.list_va(request)


@router.get(
    "/reward_summary",
)
@timeit
async def reward_summary(
    request: Annotated[DGWithUserName, Depends()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `Reward Summary API Digipos`."""
    return await account_service.reward_summary(request)


@router.get(
    "/banner",
)
@timeit
async def banner(
    request: Annotated[DGWithUserName, Depends()],
    account_service: DGAccountServices = Depends(get_dgaccount_service),
):
    """Command To `Banner API Digipos`."""
    return await account_service.banner(request)


@router.get("/test-raise")
async def test_raise():
    """Endpoint untuk testing error manual."""
    raise HTTPGenericError(message="Manual test error", context={"url": "http://dummy"})
