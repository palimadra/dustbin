import tornado.web as web
import dustbin.config as config

EMAIL = "sean.fioritto@gmail.com"
USERNAME = "sean"

def get_user_cookie(secret=None, name=None, value=None):
    if not secret:
        secret = config.appsettings["cookie_secret"]

    if not name:
        name = "user"

    if not value:
        value = USERNAME
    
    return web.create_signed_value(secret, name, value)



def set_user_cookie(request, secret=None, name=None, value=None):
    request.headers.add("Set-Cookie", "user=%s" % get_user_cookie(secret, name, value))

