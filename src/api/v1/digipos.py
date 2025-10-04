"""api digipos."""

from fastapi import APIRouter, Depends

from src.deps import DepDigiposClient
from src.schemas.sch_digipos import RequestBalance, ResponseBalance

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get(path="/balance", response_model=ResponseBalance)
async def get_balance(
    digipos_client: DepDigiposClient,
    params: RequestBalance = Depends(),
) -> ResponseBalance:
    """untuk melakukan check saldo account digipos.

    `make sure account sudah di setup di config`
    """
    response_balance = await digipos_client.get_balance(params)
    return response_balance
