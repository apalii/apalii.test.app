from aiohttp import web

from app import settings
from app.main import create_app


if settings.DEBUG:
    app = create_app()
    web.run_app(app, host=settings.HOST, port=settings.PORT)
