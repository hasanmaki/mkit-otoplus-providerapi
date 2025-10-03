"""dependencies."""

from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from src.config.settings import AppSettings


async def get_appsettings(request: Request):
    return request.app.state.settings


DepAppSettings = Annotated[AppSettings, Depends(get_appsettings)]


async def get_digipos_client(request: Request):
    return request.app.state.client_digipos


DepDigiposClient = Annotated[AsyncClient, Depends(get_digipos_client)]
