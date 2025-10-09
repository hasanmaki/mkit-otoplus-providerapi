# ruff :noqa
from typing import Annotated


from src.core.client.base_manager import HttpClientManager
from services.client.response import ResponseHandlerFactory
from fastapi import Depends, Request
from httpx import AsyncClient

from src.core.config.settings import AppSettings


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


def get_response_parser_factory() -> ResponseHandlerFactory:
    """Dependency provider buat ResponseParserFactory."""
    return ResponseHandlerFactory()


# Annotated
from typing import Annotated

DepResponseParserFactory = Annotated[
    ResponseHandlerFactory, Depends(get_response_parser_factory)
]
