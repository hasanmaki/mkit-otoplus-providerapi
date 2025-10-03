"""api digipos."""

from fastapi import APIRouter

from src.deps import DepDigiposClient

router = APIRouter(prefix="/digipos", tags=["digipos"])


@router.get("/balance")
async def get_balance(digipos_client: DepDigiposClient):
    return await digipos_client.get_balance()
