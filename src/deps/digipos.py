from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from config import AppSettings, DigiposConfig
from core.client import HttpClientService
from deps.factory import client_factory, get_appsettings, http_service_factory


def get_digipos_config(settings: AppSettings) -> DigiposConfig:
    """For future per-service config extension."""
    return settings.digipos


DepDigiposSettings = Annotated[
    DigiposConfig, Depends(lambda s=Depends(get_appsettings): s.digipos)
]

DepDigiposApiClient = Annotated[
    AsyncClient, Depends(client_factory(lambda s: s.digipos))
]

DepDigiposHttpService = Annotated[
    HttpClientService, Depends(http_service_factory(lambda s: s.digipos))
]
