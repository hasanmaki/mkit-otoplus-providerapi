from src.api.v1.dev import router as router_dev
from api.v1.dgp_account import router as router_digipos


def register_api_v1(app):
    app.include_router(router_digipos)
    app.include_router(router_dev)
    return app
