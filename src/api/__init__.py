from src.api.v1.digipos import router as router_digipos


def register_api_v1(app):
    app.include_router(router_digipos)
    return app
