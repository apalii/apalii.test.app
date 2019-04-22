## How to run a development server

Just create your virtual environment (venv/pyenv/pipenv etc) and install all the needed packages

`pip install -r requirements.txt`

Run the application using the following command:
 
`DEBUG=True python run.py`

BTW ngrok will be quite useful for the port forwarding : https://dashboard.ngrok.com/auth

## Production deployment
#### Choose your cloud provider

Feel free to use any of cloud provider such as CoogleCloud, AWS, Microsoft Azure etc. 
But I am going to show you how to deploy Python app on Digital Ocean VPS hosting, 
we are going to use Linux Ubuntu 18.04 LTS version.

#### Creating a VPS
I assume that you already signed up on Digital Ocean. 
So, log in and then press Create Droplet at the very top.

Scroll down and choose a data center. Usually I prefer Frankfunt due to lowest ping rate 
for Ukraine. When everything is ready, press Create button. 
Your droplet (VPS) is going to be ready within 60 seconds, 
you will find remote access credentials on your mailbox.

Let's log in to the terminal and update the packages:
```bash
# apt-get update
# apt-get -y upgrade
```
And then create a sudo user:
```bash
# adduser python
# adduser python sudo
```

When sudo user has been added, log in under this user called `python`.
Let's now install packages that we are going to use for deployment:
```bash
# su - python
$ sudo apt-get install -y build-essential
$ sudo apt-get install -y python-dev libreadline-dev libbz2-dev libssl-dev libsqlite3-dev libxslt1-dev libxml2-dev
```
Python 3.7 needs libffi headers to build on Linux, so :
```bash
$ sudo apt-get install libffi-dev
```

I am going to use pyenv to install the latest Python version 
(I usually do not work with system python when it comes to custom scripts and web apps). 
If you do not know what is Pyenv and how to work with it, take a look at Used libs at the very bottom.

```bash
$ pyenv install 3.7.3
```
It takes some time to download, compile and install newest version of Python, please be patient

```bash
$ cd ~
$ git clone https://github.com/apalii/dr-apalii-test-app.git
$ cd dr-apalii-test-app/
```

Configure isolated python virtual environment using pyenv.

```
$ pyenv virtualenv 3.7.3 self-rep-app
$ pyenv local self-rep-app
```
Recheck that everything works correctly:
```
root@andrii:~# .  /home/python/.pyenv/versions/3.7.3/envs/self-rep-app/bin/activate
(self-rep-app) root@andrii:~# python -V
Python 3.7.3

(self-rep-app) root@andrii:~# deactivate
root@andrii:~# python -V
Python 2.7.15rc1

root@andrii:~# python3 -V
Python 3.6.7
```
It is time to install dependencies using pip.
```
pip install -r requirements.txt
```
Recheck that all the packages have been installed properly:
```
root@andrii:~# ls /home/python/.pyenv/versions/3.7.3/envs/self-rep-app/lib/python3.7/site-packages | egrep "aio|uvl"
aiohttp
aiohttp-3.5.4.dist-info
aiohttp_cache
aiohttp_cache-1.0.3-py3.7.egg-info
aiohttp_jinja2
aiohttp_jinja2-1.1.0.dist-info
aioredis
aioredis-1.2.0.dist-info
uvloop
uvloop-0.12.2.dist-info
```


#### Setting up Nginx webserver 
It is time to set up a proxy webserver for our Django app. 
I decided to take nginx which is one of the most robust web servers and is considered 
as a best practice when it comes to deployment to production environment. 
Nginx will proxy all incomming requests to our application which is going to be served 
by WSGI server called Gunicorn. Let's take a look at the config file:

```
$ sudo apt-get install -y nginx
$ sudo systemctl stop nginx
```
We need to stop web server so that let's encrypt will be able to bind port 80 and obtain the certs.
Also  make sure that http ports are opened :
```
# nmap -p 80,443 142.93.175.145

PORT    STATE SERVICE
80/tcp  open  http
443/tcp open  https
```

#### Setting up domain name and valid SSL certificate
In order to get free of charge domain name I am going to use https://nic.ua domain registrator
and `pp.ua` domain zone. After registration of the domain .pp.ua you will have to activate it, 
just follow the hints.

After the successful activation create the appropriate `A` record with IP address of your VPS 
server. Keep in mind that changing this data may effect on work of the domain. 
Сhanges will take effect immediately, 
but there may be delays because of caching at internet-providers.

Finally let's obtain a valid SSL certificate using free service called Let's Encrypt:

```
cd ~
$ git clone https://github.com/letsencrypt/letsencrypt
$ ./letsencrypt-auto certonly --standalone -d selfreplicateapp.pp.ua
```
You should see the following output:
```
IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/selfreplicateapp.pp.ua/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/selfreplicateapp.pp.ua/privkey.pem
```
Keep in mind that certs will be valid only for 3 month. Let's continue with web server:
```
$ cd /etc/nginx/sites-available/
$ sudo nano app.conf
```
So, let's create a simple config file:
```
server {
        listen 80;
        listen 443 ssl;
        server_name selfreplicateapp.pp.ua;
        ssl_certificate /etc/letsencrypt/live/selfreplicateapp.pp.ua/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/selfreplicateapp.pp.ua/privkey.pem;
        location / {
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_pass http://localhost:8000/;
    }
}
```
Do not forget to replace a hostname! Now we have to start a server.
One important thing which you should learn before we go ahead that sites-* folders are 
managed by nginx_ensite and nginx_dissite. 
For Apache httpd users who find this with a search, the equivalents is 
a2ensite/a2dissite.

The sites-available folder is for storing all of your vhost configurations, 
whether or not they're currently enabled.

The sites-enabled folder contains symlinks to files in the sites-available 
folder. This allows you to selectively disable vhosts by removing the symlink.
```bash
$ cd /etc/nginx/sites-enabled/
$ sudo ln -s ../sites-available/app.conf app.conf
$ sudo service nginx start
```

#### Gunicorn development mode
Now it's time to configure Gunicorn.
```bash
gunicorn run:create_app --bind localhost:8000 --workers 1 --worker-class aiohttp.GunicornUVLoopWebWorker
```
We will use an alternative asyncio event loop uvloop, 
you can use the aiohttp.GunicornUVLoopWebWorker worker class.

See also https://docs.aiohttp.org/en/stable/deployment.html#start-gunicorn

Do not forget about env vars like `DEBUG=True gunicorn ...`

#### Create a Gunicorn systemd Service File
We should implement a more robust way of starting and stopping the application server. 
To accomplish this, we'll make a systemd service file.

##### Prepare GitHub app parameters

* Register app in your GitHub account https://github.com/settings/developers
* Copy `client_id` and `client_secret`
* Set `client_id` and `client_secret` environment variables in systemd unit file

Create and open a systemd service file for Gunicorn with sudo privileges in your text editor:
Gunicorn config file:

```
$ sudo nano /etc/systemd/system/gunicorn.service
```
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
Environment=DEBUG=False
Environment=CLIENT_ID=your_client_id
Environment=CLIENT_SECRET=your_clien_secret
User=python
Group=www-data
WorkingDirectory=/home/python/dr-apalii-test-app/
ExecStart=/home/python/.pyenv/versions/3.7.3/envs/self-rep-app/bin/gunicorn run:create_app --bind unix:/home/python/dr-apalii-test-app/app.sock --workers 1 --worker-class aiohttp.GunicornUVLoopWebWorker

[Install]
WantedBy=multi-user.target
```
Recheck that everithing configured properly:
```bash
$ sudo systemctl status gunicorn

● gunicorn.service - gunicorn daemon
   Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
   Active: active (running) since Mon 2019-04-22 19:38:25 UTC; 5s ago
```

#### Advanced http security settings

So, let's modify our app.conf a bit :

```
ssl_protocols TLSv1.3;# Requires nginx >= 1.13.0 else use TLSv1.2
ssl_prefer_server_ciphers on; 
ssl_dhparam /etc/nginx/dhparam.pem; # openssl dhparam -out /etc/nginx/dhparam.pem 4096
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
ssl_ecdh_curve secp384r1; # Requires nginx >= 1.1.0
ssl_session_timeout  10m;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off; # Requires nginx >= 1.5.9
ssl_stapling on; # Requires nginx >= 1.3.7
ssl_stapling_verify on; # Requires nginx => 1.3.7
resolver $DNS-IP-1 $DNS-IP-2 valid=300s;
resolver_timeout 5s; 
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```
The above ciphers are Copy Pastable in your nginx config. 
These provide Strong SSL Security for all modern browsers, plus you get an A+ 
on the SSL Labs Test. In short, they set a strong Forward Secrecy enabled 
ciphersuite, they disable SSLv2 and SSLv3, add `HTTP Strict Transport Security` 
and `X-Frame-Deny` headers and enable OCSP Stapling. Final configuration is the following:

Also we want to disables emitting nginx version on error pages and in the “Server” 
response header field `server_tokens off`.

```
server_tokens off;

server {
    listen 80;
    listen [::]:80;
    server_name selfreplicateapp.pp.ua www.selfreplicateapp.pp.ua;
    return 301 https://selfreplicateapp.pp.ua$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name www.selfreplicateapp.pp.ua;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/selfreplicateapp.pp.ua/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/selfreplicateapp.pp.ua/privkey.pem;

    return 301 https://selfreplicateapp.pp.ua$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name selfreplicateapp.pp.ua;
    client_max_body_size 1m;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/selfreplicateapp.pp.ua/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/selfreplicateapp.pp.ua/privkey.pem;

    ssl_protocols TLSv1.3;# Requires nginx >= 1.13.0 else use TLSv1.2
    ssl_prefer_server_ciphers on;
    ssl_dhparam /etc/nginx/dhparam.pem; # openssl dhparam -out /etc/nginx/dhparam.pem 4096
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_ecdh_curve secp384r1; # Requires nginx >= 1.1.0

    ssl_session_timeout  10m;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off; # Requires nginx >= 1.5.9

    ssl_stapling on; # Requires nginx >= 1.3.7
    ssl_stapling_verify on; # Requires nginx => 1.3.7

    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_pass http://unix:/home/python/dr-apalii-test-app/app.sock;
    }

    location /static {
      # path for static files
      root /home/python/dr-apalii-test-app/app/static;
    }
}
```

## Used libs
* https://github.com/pyenv/pyenv
* http://docs.gunicorn.org/en/stable/
* https://aiohttp.readthedocs.io/
* https://aiohttp-cache.readthedocs.io/
* https://aiohttp-jinja2.readthedocs.io/en/stable/


## Used resources
* http://nginx.org/en/docs/http/ngx_http_core_module.html
* https://cipherli.st/
* https://www.ssllabs.com/ssltest/analyze.html?d=selfreplicateapp.pp.ua
* https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04#create-a-gunicorn-systemd-service-file
* https://khashtamov.com/en/how-to-deploy-telegram-bot-django/
* https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html

## Info
I've decided to use async libs and cache because there are external calls to 3rd party 
resource (github API), and it takes about 5 seconds per request.
