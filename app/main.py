import asyncio

import uvloop
from aiohttp import web
from aiohttp_cache import setup_cache

from app.resources import init_jinja, init_web_client
from app.routes import setup_routes

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def create_app() -> (web.Application, str, str):
    app = web.Application()

    setup_routes(app)
    setup_cache(app)
    setup_cleanup_ctx(app, [init_jinja, init_web_client])

    return app


def setup_cleanup_ctx(app, startup_cleanup_funcs):
    for f in startup_cleanup_funcs:
        app.cleanup_ctx.append(f)
