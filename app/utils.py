import os
from base64 import b64encode

import aiohttp
import aiohttp_jinja2

from aiohttp import web


def get_repo(base_dir):
    repo = {}
    exclude = {'__pycache__', 'venv', '.idea', '.git'}
    for root, dirs, files in os.walk(base_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file in {'.DS_Store', 'favicon.ico'}:
                continue
            root_path = root.split('dr-apalii-test-app')[-1]
            with open(os.path.join(root, file), 'rb') as f:
                content = b64encode(f.read()).decode("utf-8")
                path = os.path.join(root_path.lstrip('/'), file)
                repo[path] = content
    return repo


def template(template_name, request, context=None):
    return aiohttp_jinja2.render_template(template_name, request, context)


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)


class WebClient:
    """
    Simple async web client which implements GET and POST methods
    https://docs.aiohttp.org/en/stable/client_quickstart.html#make-a-request
    """
    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def get(self, url, data_type='json', headers=None):
        async with self._session.get(url, ssl=True, headers=headers) as response:
            if data_type == 'text':
                return await response.text()
            return await response.json()

    async def post(self, url, data_type='json', data=None, json=None, headers=None):
        async with self._session.post(url, ssl=True, data=data, json=json, headers=headers) as response:
            if data_type == 'text':
                return await response.text()
            return await response.json()

    async def put(self, url, data_type='json', data=None, json=None, headers=None):
        async with self._session.put(url, ssl=True, data=data, json=json, headers=headers) as response:
            if data_type == 'text':
                return await response.text()
            return await response.json()

    async def close(self):
        await self._session.close()

