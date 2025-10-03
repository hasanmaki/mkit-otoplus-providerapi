from urllib.parse import urljoin


def build_url(base_url: str, endpoint: str) -> str:
    """Gabungkan base_url dengan endpoint secara aman."""
    return urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))
