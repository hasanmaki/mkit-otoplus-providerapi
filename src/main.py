import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.api import register_api_v1
from src.config.cfg_logging import setup_logging
from src.config.settings import get_settings
from src.custom.exceptions import AppExceptionError, global_exception_handler
from src.custom.middlewares import LoggingMiddleware
from src.services.clients.manager import ApiClientManager

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.INFO)
setup_logging()

settings = get_settings()


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Application startup")
    client_manager = ApiClientManager()
    app.state.settings = settings
    app.state.api_manager = client_manager
    await client_manager.start()
    logger.bind(settings=settings).debug("Settings loaded")
    yield
    await client_manager.stop()
    app.state.api_manager = None
    app.state.settings = None
    logger.debug("Application shutdown")


app = FastAPI(lifespan=lifespan)

# register middleware
app.add_middleware(LoggingMiddleware)

# register exception
app.add_exception_handler(AppExceptionError, global_exception_handler)  # type: ignore

# register routers
register_api_v1(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app="src:main.app", host="0.0.0.0", port=8000, reload=True)
