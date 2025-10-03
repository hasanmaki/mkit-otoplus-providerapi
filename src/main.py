from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from httpx import AsyncClient
from loguru import logger

from src.config.cfg_logging import setup_logging
from src.config.settings import get_settings
from src.custom.exceptions import AppExceptionError, global_exception_handler
from src.custom.middlewares import LoggingMiddleware

setup_logging()

settings = get_settings("config.toml")


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Application startup")
    app.state.settings = settings
    app.state.client_digipos = AsyncClient(
        base_url=settings.digipos.base_url,
        headers=settings.digipos.headers,
        timeout=settings.digipos.timeout,
        http2=settings.digipos.http2,
    )
    logger.bind(settings=settings).debug("Settings loaded")
    yield
    await app.state.client_digipos.aclose()
    logger.debug("Application shutdown")


app = FastAPI(lifespan=lifespan)

# register middleware
app.add_middleware(LoggingMiddleware)

# regisrer exception
app.add_exception_handler(AppExceptionError, global_exception_handler)  # type: ignore


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app="src:main.app", host="0.0.0.0", port=8000, reload=True)
