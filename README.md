## How to run a development server

Just create your virtual environment (venv/pyenv/pipenv etc) and install all the needed packages

`pip install -r requirements.txt`

Run the application using the following command:
 
`DEBUG=True python run.py`


## Production deployment
#### Choose your cloud provider


## Used libs
* https://aiohttp.readthedocs.io/
* https://aiohttp-cache.readthedocs.io/
* https://aiohttp-jinja2.readthedocs.io/en/stable/

## Info
I've decided to use async libs and cache because there are external calls to 3rd party 
resource (github API), and it takes about 5 seconds per request.
