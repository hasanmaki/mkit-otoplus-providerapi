from httpx import AsyncClient

from src.config.cfg_api_clients import ApiBaseConfig
from src.core.client import ApiClientManager, HttpClientFactory


def build_and_register(
    manager: ApiClientManager, name: str, config: ApiBaseConfig
) -> AsyncClient:
    """Build AsyncClient dari config dan register ke manager sekaligus."""
    client = HttpClientFactory.create_client(config)
    manager.register_client(name, client)
    return client
