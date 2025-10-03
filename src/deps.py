# src/dependencies.py
from typing import Annotated

from fastapi import Depends, Request

from src.config.cfg_api_clients import DigiposConfig
from src.config.settings import AppSettings
from src.core.clients.digipos import DigiposApiClient


async def get_appsettings(request: Request) -> AppSettings:
    return request.app.state.settings


async def get_digipos_config(
    settings: AppSettings = Depends(get_appsettings),
) -> DigiposConfig:
    return settings.digipos


async def get_digipos_api_client(
    request: Request, config: DigiposConfig = Depends(get_digipos_config)
) -> DigiposApiClient:
    httpx_client = request.app.state.client_digipos
    return DigiposApiClient(client=httpx_client, config=config)


DepDigiposClient = Annotated[DigiposApiClient, Depends(get_digipos_api_client)]
