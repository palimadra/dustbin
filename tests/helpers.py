import tornado.web as web
import dustbin.config as config
import os.path as path
import dustbin.api.model as model
from dustbin.api import Application
from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders


EMAIL = "sean.fioritto@test.com"
SUBDOMAIN = "sean"

def get_user_cookie(secret=None, name=None, value=None):
    if not secret:
        secret = config.appsettings["cookie_secret"]

    if not name:
        name = "user"

    if not value:
        a = model.Account(subdomain=SUBDOMAIN, email=EMAIL)
        value = a.url
    
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
    

class BaseTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application()


    def create_post(self, uri="/posts", post=None):
        if not post:
            post = model.Post("text is something like this.\nplus a paragraph",
                              title="title here",
                              prefix = url(uri))
    
        headers = set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        created = self.fetch(url(uri),
                             method="POST",
                             body=post.json,
                             headers=headers)
        return post, created


