import logging

from aiohttp import web
from aiohttp_cache import cache

from app.utils import template
from app import settings


if settings.DEBUG:
    logging.basicConfig(level=logging.DEBUG)


@cache(expires=settings.DAY)
async def index(request):
    context = {'domain': settings.DOMAIN}
    response = template('index.html', request, context=context)
    return response


class GitHubAuthView(web.View):
    async def get(self):
        app = self.request.app

        redirect_uri = '{}{}'.format(settings.DOMAIN, app.router['github-callback'].url_for())
        github_url_params = "{}?client_id={}&redirect_uri={}&scope={}".format(
            settings.GITHUB_AUTH_URL,
            settings.CLIENT_ID,
            redirect_uri,
            settings.SCOPE
        )
        return web.HTTPFound(github_url_params)


class GitHubCallbackView(web.View):

    @staticmethod
    def get_auth_headers(token):
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    async def fetch_token(self, code):
        """Fetches token with code parameter
        """
        web_client = self.request.app['web_client']
        token_url = 'https://github.com/login/oauth/access_token'
        data = {
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'code': code
        }
        headers = {'Accept': 'application/json'}
        token = await web_client.post(token_url, data=data, headers=headers)
        return token['access_token']

    async def fetch_user_info(self, token):
        """Fetches user information by token
        """
        web_client = self.request.app['web_client']
        url = 'https://api.github.com/user'
        headers = {'Authorization': f'Bearer {token}'}
        return await web_client.get(url, headers=headers)

    async def create_repo(self, token, repo_name):
        """Creates repo in user's GitHub account
        """
        web_client = self.request.app['web_client']
        headers = self.get_auth_headers(token)
        data = {
            'name': repo_name,
            'description': f'Self replicating app from {settings.REPO_LINK}',
            'private': False
        }
        url = 'https://api.github.com/user/repos'
        repo_created = await web_client.post(url, headers=headers, json=data)
        return repo_created

    async def create_file(self, token,  user_name, file_path, file_content):
        """Writes all the needed files to user`s GitHub repo
        """
        repo_name = settings.REPO_NAME
        web_client = self.request.app['web_client']
        url = f'https://api.github.com/repos/{user_name}/{repo_name}/contents/{file_path}'
        headers = self.get_auth_headers(token)
        data = {
            'message': f'Adding {file_path}',
            'content': file_content
        }
        result = await web_client.put(url, headers=headers, json=data)
        return result

    async def get(self):
        code = self.request.query.get('code', None)
        if code is None:
            return web.json_response({"errors": "Can't fetch token"}, status=400)
        token = await self.fetch_token(code)
        user = await self.fetch_user_info(token)
        user_name, user_redirect_url = user['login'], user['url']
        repo = await self.create_repo(token, settings.REPO_NAME)
        if 'errors' in repo:
            error = {'error': repo['message'], 'domain': settings.DOMAIN}
            return template('errors.html', self.request, context=error)
        repo_files = settings.REPO
        for file in repo_files.keys():
            await self.create_file(token, user_name, file, repo_files[file])
        return web.HTTPFound(repo['html_url'])
