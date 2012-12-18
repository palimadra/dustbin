import dustbin.config as config
import json
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from dustbin.api.model import Post, Feed

#(?:/?$)?|
urlpatterns = {
    "NewPostHandler" : r"/(?P<subdomain>[^/]+)/(?:private|public)/(?:(?P<lense>[^/]+)/posts|posts)/?$",
    "PostsHandler" : r"/(?P<subdomain>[^/]+)/(?:private|public)/(?:posts|[^/]+/posts)/.+",
    "FeedsHandler" : r"/(?P<subdomain>[^/]+)/(?:private|public)/(?:feed|[^/]+/feed)(?:\.json)?/?$",
}


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
            (urlpatterns["NewPostHandler"], NewPostHandler),
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
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.db.get(user_id)


class NewPostHandler(BaseHandler):

    @authorized
    @tornado.web.authenticated
    def post(self, subdomain, lense=None):
        post = Post(**json.loads(self.request.body))
        post.prefix = self.request.uri
        post.save(db=self.db)

        url = Feed.get_url(post.prefix)
        try:
            feed = Feed(db=self.db).load(url + '.json')
        except:
            feed == Feed(db=self.db,
                         prefix=prefix,
                         author=self.current_user)
            feed.save()
                         
        self.set_header("Location", post.url)
        self.set_status(201)
        

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
