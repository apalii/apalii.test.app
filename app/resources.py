import aiohttp_jinja2
import jinja2

from app.utils import WebClient


async def init_jinja(app):
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('app'))
    yield


async def init_web_client(app):
    """
    Most likely you need a session per application which performs all requests altogether.
    """
    app['web_client'] = WebClient()
    yield
    await app['web_client'].close()
