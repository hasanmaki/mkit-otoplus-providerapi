from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from src.config.cfg_api_clients import DigiposConfig
from src.config.settings import AppSettings
from src.services.clients.manager import ApiClientManager
from src.services.digipos.srv_accounts import ServiceDigiposAccount


async def get_appsettings(request: Request) -> AppSettings:
    """dependency to get app settings."""
    return request.app.state.settings


DepAppSettings = Annotated[AppSettings, Depends(get_appsettings)]


async def get_app_digipos_settings(
    settings: AppSettings = Depends(get_appsettings),
) -> DigiposConfig:
    return settings.digipos


DepDigiposSettings = Annotated[DigiposConfig, Depends(get_app_digipos_settings)]


def get_api_manager(request: Request) -> ApiClientManager:
    """dependency to get api manager.

    get the client manager from app state."""
    return request.app.state.api_manager


async def get_digipos_client(
    manager: ApiClientManager = Depends(get_api_manager),
) -> AsyncClient:
    """get digipos client from api manager.(api manager is from app state)"""
    return manager.get_client("digipos")


DepDigiposApiClient = Annotated[AsyncClient, Depends(get_digipos_client)]


async def get_digipos_account_service(
    digipos_client: DepDigiposApiClient,
    appsettings: DepAppSettings,
    digipos_settings: DepDigiposSettings,
) -> ServiceDigiposAccount:
    return ServiceDigiposAccount(client=digipos_client, config=digipos_settings)
