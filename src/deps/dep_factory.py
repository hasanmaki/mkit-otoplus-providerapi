# ruff :noqa
from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from src.config.settings import AppSettings
from src.core.client import HttpClientManager, HttpClientService


async def get_appsettings(request: Request) -> AppSettings:
    """Ambil AppSettings dari state FastAPI."""
    return request.app.state.settings


DepAppSettings = Annotated[AppSettings, Depends(get_appsettings)]


def get_api_manager(request: Request) -> HttpClientManager:
    """Ambil ApiClientManager dari app state."""
    return request.app.state.api_manager


DepApiManager = Annotated[HttpClientManager, Depends(get_api_manager)]


def client_factory(config_getter):
    """Factory untuk generate AsyncClient dari AppSettings."""

    async def _dep(
        settings: AppSettings = Depends(get_appsettings),
        manager: HttpClientManager = Depends(get_api_manager),
    ) -> AsyncClient:
        config = config_getter(settings)
        return manager.get_client(config.name)

    return _dep


def http_service_factory(config_getter):
    """Factory untuk generate HttpClientService dari AppSettings."""

    async def _dep(
        client: AsyncClient = Depends(client_factory(config_getter)),
        settings: AppSettings = Depends(get_appsettings),
    ) -> HttpClientService:
        config = config_getter(settings)
        return HttpClientService(client, config.name)

    return _dep
