import dustbin.config as config
import json
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from model import Post, Feed, Account
from urls import urlpatterns

def authorized(fn):
    def wrapped(*args, **kwargs):
        self = args[0]
        # TODO: use self.current_user to authorize,
        # for now everything is good
        if True:
            fn(*args, **kwargs)
        else:
            raise tornado.web.HTTPError(403)
            
    return wrapped


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (urlpatterns["PostsHandler"], PostsHandler),
            (urlpatterns["FeedHandler"], FeedHandler),
        ]
        settings = config.appsettings
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = config.get_db()
        

class BaseHandler(tornado.web.RequestHandler):
    
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        accounturl = self.get_secure_cookie("user")
        if not accounturl: return None
        return Account().load(accounturl, db=self.db)


class FeedHandler(BaseHandler):

    @authorized
    @tornado.web.authenticated
    def post(self, subdomain, lense=None):
        post = Post(**json.loads(self.request.body))
        post.prefix = self.request.uri
        post.save(self.current_user, db=self.db)
        self.set_header("Location", post.url)
        self.set_status(201)

    @authorized
    @tornado.web.authenticated
    def get(self, subdomain, lense=None):
        return self.write(self.db.get(self.request.uri))
        

class PostsHandler(BaseHandler):
    
    @authorized
    @tornado.web.authenticated
    def get(self, subdomain):
        url = self.request.uri
        if self.request.headers["Content-type"] == "text/html":
            if not url.endswith(".html"):
                url = url + ".html"
            self.write(self.db.get(url))
        else:
            if not url.endswith(".json"):
                url = url + ".json"
            self.write(self.db.get(url))
