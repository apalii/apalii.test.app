from enum import Enum

from aiohttp import web

from app.views.main import index, GitHubAuthView, GitHubCallbackView


class Method(str, Enum):
    POST = 'POST'
    GET = 'GET'


views = [
    {'path': '/repl', 'handler': GitHubAuthView, 'name': 'github-repl'},
    {'path': '/callback', 'handler': GitHubCallbackView, 'name': 'github-callback'},
]

urls = [
    {'method': Method.GET, 'path': '/', 'handler': index, 'name': 'index'},
]


def setup_routes(app: web.Application) -> None:
    router = app.router

    router.add_static('/assets', 'app/static', name='static')

    for url in urls:
        router.add_route(**url)

    routes = []

    for view in views:
        routes.append(web.view(**view))

    router.add_routes(routes)
