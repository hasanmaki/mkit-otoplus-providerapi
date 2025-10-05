from typing import Any

from domain.digipos.services.trim_service import ProductListResponse
from src.core.service_request import CoreApiRequestService
from src.core.service_response import context_to_dict
from src.domain.digipos.schemas import DGTrxListPaket, TrxAuthPayload


# later use and extend , for now we are experimenting.
def extract_payload(request: DGTrxListPaket) -> dict:
    """Extract payload from request, excluding auth fields."""
    exclude_fields = set(TrxAuthPayload.model_fields.keys()) - {"product"}
    return request.model_dump(exclude=exclude_fields)


def build_list_paket_query(request: DGTrxListPaket) -> dict:
    """Build query params for list_paket Digipos API."""
    return {
        "username": request.username,  # dari request
        "category": request.product,  # dari request
        "to": request.dest,  # dari request
        "up_harga": request.up_harga,
        "json": 1,
        "payment_method": "LINKAJA",  # hardcoded
        "kolom": "productId,productName,quota,total_",  # hardcoded
    }


class DGTransactionService(CoreApiRequestService):
    async def get_list_paket(self, request: DGTrxListPaket) -> Any:
        params = build_list_paket_query(request)
        raw_response = await self._send(
            "GET", self.settings.endpoints.list_paket, params
        )
        # Normalisasi dan parsing ke model
        parsed_response = ProductListResponse(
            **context_to_dict(self.settings, raw_response)
        )
        # Formatting response
        if request.totext == 1:
            return parsed_response.to_text()
        return parsed_response.model_dump()
