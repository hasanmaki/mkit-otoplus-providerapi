# # src/core/clients/manager.py
# from typing import Dict

# import httpx
# from httpx_retries import Retry, RetryTransport
# from loguru import logger
# from aiolimiter import AsyncLimiter

# from src.config.settings import get_settings


# class ApiClientManager:
#     """
#     Centralized async HTTP client manager:
#     - Retry aware (with callback logging)
#     - Rate limited per-host (via AsyncLimiter)
#     - Connection pooling (httpx.Limits)
#     """

#     def __init__(self) -> None:
#         self._clients: Dict[str, httpx.AsyncClient] = {}
#         self._limiters: Dict[str, AsyncLimiter] = {}
#         self.log = logger.bind(context="ApiClientManager")
#         self.settings = get_settings()

#     # -------------------------------------------------------------------------
#     # Retry callback (buat log setiap attempt)
#     # -------------------------------------------------------------------------
#     @staticmethod
#     async def _log_retry_attempt(attempt: int, exc: Exception, delay: float) -> None:
#         logger.warning(
#             f"[HTTP RETRY] Attempt {attempt} after {delay:.2f}s due to {exc.__class__.__name__}: {exc}"
#         )

#     # -------------------------------------------------------------------------
#     # Lifecycle
#     # -------------------------------------------------------------------------
#     async def start(self) -> None:
#         """Init semua HTTP client + limiter global."""
#         self.log.info("Initializing HTTP clients...")

#         retry = Retry(
#             total=5,
#             backoff_factor=0.5,
#             status_forcelist=[429, 500, 502, 503, 504],
#             allowed_methods=["GET", "POST"],
#             callback=self._log_retry_attempt,  # <--- log tiap retry
#         )

#         transport = RetryTransport(retry=retry)

#         limits = httpx.Limits(
#             max_keepalive_connections=100,
#             max_connections=100,
#             keepalive_expiry=300,
#         )

#         digipos_cfg = self.settings.digipos

#         await self.register_client(
#             name="digipos",
#             base_url=str(digipos_cfg.base_url),
#             headers=digipos_cfg.headers,
#             timeout=digipos_cfg.timeout,
#             http2=digipos_cfg.http2,
#             transport=transport,
#             limits=limits,
#             rate_limit_per_sec=5,  # contoh: max 5 request per detik
#         )

#         self.log.success(f"Registered clients: {list(self._clients.keys())}")

#     # -------------------------------------------------------------------------
#     # Register client
#     # -------------------------------------------------------------------------
#     async def register_client(
#         self,
#         name: str,
#         base_url: str,
#         headers: dict,
#         timeout: float | int,
#         http2: bool = False,
#         *,
#         transport: httpx.AsyncBaseTransport | None = None,
#         limits: httpx.Limits | None = None,
#         rate_limit_per_sec: int | None = None,
#     ) -> None:
#         """Register client + optional rate limiter per host."""
#         if name in self._clients:
#             self.log.warning(f"Client '{name}' sudah terdaftar — dilewati.")
#             return

#         client = httpx.AsyncClient(
#             transport=transport,
#             base_url=base_url,
#             headers=headers,
#             timeout=timeout,
#             http2=http2,
#             limits=limits,
#         )
#         self._clients[name] = client

#         if rate_limit_per_sec:
#             self._limiters[name] = AsyncLimiter(rate_limit_per_sec, time_period=1)
#             self.log.debug(f"Limiter aktif untuk '{name}' ({rate_limit_per_sec}/s)")

#         self.log.debug(
#             f"HTTP client '{name}' initialized | base_url={base_url} | "
#             f"retry={getattr(transport, 'retry', None)}"
#         )

#     # -------------------------------------------------------------------------
#     # Helper akses client + limiter
#     # -------------------------------------------------------------------------
#     def get_client(self, name: str) -> httpx.AsyncClient:
#         if name not in self._clients:
#             self.log.error(f"Client '{name}' belum diinisialisasi")
#             raise ValueError(f"Client '{name}' belum diinisialisasi")
#         return self._clients[name]

#     def get_limiter(self, name: str) -> AsyncLimiter | None:
#         """Ambil limiter per client (optional)."""
#         return self._limiters.get(name)

#     # -------------------------------------------------------------------------
#     # Shutdown
#     # -------------------------------------------------------------------------
#     async def stop(self) -> None:
#         """Tutup semua koneksi saat app shutdown."""
#         self.log.info("Closing HTTP clients...")
#         for client in self._clients.values():
#             await client.aclose()
#         self._clients.clear()
#         self._limiters.clear()
#         self.log.success("All HTTP clients closed successfully.")
