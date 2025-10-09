"""Kesimpulan!

Setiap kali Anda menggunakan model Pydantic sebagai parameter fungsi di dalam FastAPI (baik itu fungsi endpoint atau fungsi dependency), Anda harus secara eksplisit memberi tahu FastAPI bagaimana cara mendapatkannya:

- Depends(...): Jika itu adalah objek yang harus disuntikkan (dependency).

- Body(...) (atau tidak ada wrapper): Jika itu adalah data JSON dari Request Body.

- Query(...), Path(...), ``Header(...)`: Jika itu berasal dari URL atau header.

Dengan menambahkan = Depends(get_app_settings) pada parameter settings di get_digipos_config, Anda memastikan bahwa:

Objek AppSettings diinjeksikan dengan benar.

FastAPI tahu bahwa itu adalah dependensi, bukan Request Body, dan akan menyembunyikannya dari dokumentasi kecuali ia adalah root dari endpoint itu sendiri.
"""

from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from servicess.client.request import HttpRequestService
from servicess.client.response import ResponseHandlerFactory
from src.core.config.cfg_api_clients import DigiposConfig
from src.core.config.settings import AppSettings
from src.deps.dep_factory import (
    client_factory,
    get_appsettings,
    get_response_parser_factory,
)
from src.servicess.digipos.auth_service import DigiposAuthService
from src.servicess.digipos.command_service import DGCommandServices


def get_digipos_config(
    settings: AppSettings = Depends(get_appsettings),
) -> AppSettings:
    """Ambil config Digipos dari AppSettings."""
    return settings.digipos


def get_digipos_http_service(
    client: AsyncClient = Depends(client_factory(lambda s: s.digipos)),
    config: DigiposConfig = Depends(get_digipos_config),
    response_handler: ResponseHandlerFactory = Depends(get_response_parser_factory),
):
    """Generate HttpClientService khusus Digipos."""
    return HttpRequestService(
        client=client, service_name=config.name, response_handler=response_handler
    )


def get_digipos_auth_service(
    config: DigiposConfig = Depends(get_digipos_config),
) -> DigiposAuthService:
    """Generate DigiposAuthService dengan config default."""
    return DigiposAuthService(config)


def get_digipos_command_service(
    http_service: HttpRequestService = Depends(get_digipos_http_service),
    auth_service: DigiposAuthService = Depends(get_digipos_auth_service),
    config: DigiposConfig = Depends(get_digipos_config),
):
    """Generate DGCommandServices (endpoint caller) siap pakai."""
    return DGCommandServices(http_service, auth_service, config)


# Annotated Style if needed
DepDigiposSettings = Annotated[DigiposConfig, Depends(get_digipos_config)]
DepDigiposApiClient = Annotated[
    AsyncClient, Depends(client_factory(lambda s: s.digipos))
]
DepDigiposHttpService = Annotated[HttpRequestService, Depends(get_digipos_http_service)]
DepDigiposAuthService = Annotated[DigiposAuthService, Depends(get_digipos_auth_service)]
DepDigiposCommandService = Annotated[
    DGCommandServices, Depends(get_digipos_command_service)
]
