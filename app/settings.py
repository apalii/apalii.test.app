import os

from app.utils import get_repo

# Server
DEBUG = os.environ['DEBUG'] == 'True'
HOST = '127.0.0.1'
PORT = 8000
DOMAIN = 'https://selfreplicateapp.pp.ua'
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Constants
HOUR = 60 * 60
DAY = HOUR * 24

# GitHub settings
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
SCOPE = 'public_repo'

# Repository
REPO_NAME = 'self_replicate_app'
REPO_LINK = 'https://github.com/apalii/' + REPO_NAME
REPO = get_repo(BASE_DIR)
