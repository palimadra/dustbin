import tornado.web as web
import dustbin.config as config
import os.path as path

EMAIL = "sean.fioritto@gmail.com"
SUBDOMAIN = "sean"

def get_user_cookie(secret=None, name=None, value=None):
    if not secret:
        secret = config.appsettings["cookie_secret"]

    if not name:
        name = "user"

    if not value:
        value = EMAIL
    
    return web.create_signed_value(secret, name, value)


def set_user_cookie(headers, secret=None, name=None, value=None):
    headers.add("Cookie", "user=%s" % get_user_cookie(secret, name, value))
    return headers


def url(end, public=False):

    if public:
        puborpriv = "public"
    else:
        puborpriv = "private"
        
    return path.join(*(["/" + SUBDOMAIN, puborpriv] + end.split("/")))

    
    
