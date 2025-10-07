from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from loguru import logger

from src.api import register_api_v1
from src.config.cfg_logging import setup_logging
from src.config.settings import get_settings
from src.core.client.base_manager import HttpClientManager
from src.core.client.main_setup import setup_client
from src.custom.exceptions import AppExceptionError
from src.custom.middlewares import LoggingMiddleware
from src.tag import tags_metadata

setup_logging()


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager."""
    logger.debug("Application startup")
    settings = get_settings()
    client_manager = HttpClientManager()
    await setup_client(client_manager, settings.digipos)
    # add more client here

    app.state.settings = settings
    app.state.api_manager = client_manager

    await client_manager.start_all()
    logger.debug(f" settings Loadded with values {settings}")

    yield

    await client_manager.stop_all()
    app.state.api_manager = None
    app.state.settings = None
    logger.debug("Application shutdown")


app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"docExpansion": "none"},
)

# register middleware
app.add_middleware(LoggingMiddleware)


# register exception
@app.exception_handler(AppExceptionError)
async def global_exception_handler(request: Request, exc: AppExceptionError):
    """Handler dinamis untuk AppExceptionError (mendukung JSON dan TEXT)."""
    response_format = request.headers.get(
        "X-Response-Format"
    ) or request.query_params.get("format", "json")

    if response_format.lower() == "text":
        text = f"[{exc.__class__.__name__}] {exc.message}"
        if exc.context:
            text += f" | Context: {exc.context}"
        return PlainTextResponse(text, status_code=exc.status_code)

    return JSONResponse(content=exc.to_dict(), status_code=exc.status_code)


# register routers
register_api_v1(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("src:main.app", host="0.0.0.0", port=8000, reload=True)
