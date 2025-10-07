# from fastapi import APIRouter

# from deps.digipos import DepDigiposHttpService, DepDigiposSettings

# router = APIRouter(prefix="/test", tags=["test"])


# # class PlainDictResponse(Response):
# #     media_type = "text/plain"

# #     def render(self, content: NormalizedResponse | dict) -> bytes:
# #         if isinstance(content, NormalizedResponse):
# #             status = content.status_code
# #             url = content.url
# #             meta = str(content.meta).replace("'", "")
# #             message = (
# #                 content.message
# #                 if hasattr(content.message, "value")
# #                 else str(content.message)
# #             )
# #             data = str(content.data).replace("'", "")
# #             text = f"{status}&{url}&{meta}&{message}&{data}"
# #         elif isinstance(content, dict):
# #             text = str(content).replace("'", "")
# #         else:
# #             text = str(content)
# #         return text.encode("utf-8")


# @router.get("/test_service", response_class=PlainDictResponse)
# async def test(service: DepDigiposHttpService, dgsettings: DepDigiposSettings):
#     """Testing with injected service."""
#     params = {"username": dgsettings.username}
#     debug: bool = dgsettings.debug
#     endpoint: str = "balance"
#     result = await service.safe_request(
#         "GET", endpoint=endpoint, params=params, debugresponse=debug
#     )
#     return PlainDictResponse(result)


# @router.get("/test_transaksi", response_class=PlainDictResponse)
# async def test_transaction(
#     service: DepDigiposHttpService, dgsettings: DepDigiposSettings
# ):
#     """Testing with injected service."""
#     params = {
#         "username": dgsettings.username,
#         "to": "081295221639",
#         "category": "DATA",
#         "payment_method": "LINKAJA",
#         "json": 1,
#         "kolom": "productId,productName,quota,total_",
#         "up_harga": 100,
#     }
#     debug: bool = dgsettings.debug
#     endpoint: str = "list_paket"
#     result = await service.safe_request(
#         "GET", endpoint=endpoint, params=params, debugresponse=debug
#     )
#     return PlainDictResponse(result)
