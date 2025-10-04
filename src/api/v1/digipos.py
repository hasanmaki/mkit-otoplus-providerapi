# """api digipos."""

# from fastapi import APIRouter, Depends
# from fastapi.responses import PlainTextResponse

# from src.core.clients.response_utils import respond
# from src.deps import DepDigiposClient, DepDigiposSettings
# from src.schemas.sch_digipos import RequestBalance, ResponseBalance

# router = APIRouter(prefix="/digipos", tags=["digipos"])


# @router.get(path="/balance", response_model=ResponseBalance)
# async def get_balance(
#     digipos_client: DepDigiposClient,
#     settings: DepDigiposSettings,
#     params: RequestBalance = Depends(),
# ) -> PlainTextResponse | ResponseBalance:
#     """
#     untuk melakukan check saldo account digipos.
#     `make sure account sudah di setup di config`
#     """
#     response_balance = await digipos_client.get_balance(params)

#     return respond(response_balance, settings)
