"""api digipos."""

from typing import Annotated

from fastapi import APIRouter, Query

from src.deps import DepDigiposClient
from src.schemas.sch_digipos import RequestBalance, ResponseBalance

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get("/balance", response_model=ResponseBalance)
async def get_balance(
    digipos_client: DepDigiposClient,
    request_data: Annotated[RequestBalance, Query()],
):
    return await digipos_client.get_balance(request_data)
