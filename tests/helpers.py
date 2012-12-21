import tornado.web as web
import dustbin.config as config
import os.path as path
import dustbin.api.model as model
from dustbin.api import Application
from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders


EMAIL = 'sean.fioritto@test.com'
SUBDOMAIN = 'sean'

def create_author(db):
    author = model.Author(subdomain=SUBDOMAIN, email=EMAIL)
    return author.save(db=db)


def get_user_cookie(secret=None, author=None):
    if not secret:
        secret = config.appsettings['cookie_secret']

    if not author:
        name = 'user'

    if not author:
        author = model.Author(subdomain=SUBDOMAIN, email=EMAIL)
    
    return web.create_signed_value(secret, 'user', author.url)


def set_user_cookie(secret=None, contenttype='text/html', author=None):
    headers = HTTPHeaders({'Content-Type' : contenttype})
    headers.add('Cookie', 'user=%s' % get_user_cookie(secret, author=author))
    return headers


def url(end, public=False):

    if public:
        puborpriv = 'public'
    else:
        puborpriv = 'private'
        
    return path.join(*(['/' + SUBDOMAIN, puborpriv] + end.split('/')))
    

class BaseTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application()


    def create_post(self,
                    uri='/posts',
                    post=None,
                    db=None,
                    contenttype='application/json',
                    author=None):
        
        if not post:

            if not author:
                author = create_author(db)

            post = model.Post('text is something like this.\nplus a paragraph',
                              title='title here',
                              prefix = url(uri),
                              author=author,
                              db=db)
    
        headers = set_user_cookie(contenttype=contenttype)
        created = self.fetch(url(uri),
                             method='POST',
                             body=post.json,
                             headers=headers)
        return post, created

