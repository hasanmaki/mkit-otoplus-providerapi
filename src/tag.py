"""meta data tags for better classification."""

from enum import StrEnum
from typing import Any


class Tags(StrEnum):
    """Tags for API endpoints."""

    digipos = "digipos"
    digipos_account = "digipos_account"
    digipos_utils = "digipos_utils"
    digipos_transaction = "digipos_transaction"


tags_metadata: list[dict[str, Any]] = [{"name": tag} for tag in Tags]
