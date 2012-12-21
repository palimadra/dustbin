import dustbin.config as config
import json
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from model import Post, Feed, Author
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
            (urlpatterns['PostsHandler'], PostsHandler),
            (urlpatterns['FeedHandler'], FeedHandler),
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
        authorurl = self.get_secure_cookie('user')
        if not authorurl: return None
        return Author().load(authorurl, db=self.db)


class FeedHandler(BaseHandler):

    @authorized
    @tornado.web.authenticated
    def post(self, subdomain, lense=None):
        if self.request.headers['Content-type'] == 'application/json':
            post = Post(**json.loads(self.request.body))
            post.prefix = self.request.uri
            post.author = self.current_user
            post.save(db=self.db)
            self.set_header('Location', post.url)
            self.set_status(201)
        else:
            self.send_error(500)

    @authorized
    @tornado.web.authenticated
    def get(self, subdomain, lense=None):
#        import pdb; pdb.set_trace()
        return self.write(self.db.get(self.request.uri))
        

class PostsHandler(BaseHandler):
    
    @authorized
    @tornado.web.authenticated
    def get(self, subdomain):
        url = self.request.uri
        if url.endswith('/'):
            url = url[:-1]
        if self.request.headers['Content-type'] == 'text/html':
            if not url.endswith('.html'):
                url = url + '.html'

        else:
            if not url.endswith('.json'):
                url = url + '.json'

        try:
            serialized = self.db.get(url)
            self.write(serialized)
        except:
            self.set_status(404)
            

    @authorized
    @tornado.web.authenticated
    def put(self, subdomain):
        url = self.request.uri
        if url.endswith('/'):
            url = url[:-1]
        if self.request.headers['Content-type'] == 'application/json':
            if not url.endswith('.json'):
                url = url + '.json'
            try:
                post = Post(**json.loads(self.request.body))
                post.db = self.db
                if post.author == self.current_user:
                    post.save(db=self.db)
                    self.set_status(204)
                else:
                    self.set_status(403)
            except:
                self.send_error(500)
        else:
            self.send_error(500)


    @authorized
    @tornado.web.authenticated
    def delete(self, subdomain):
        url = self.request.uri
        if url.endswith('/'):
            url = url[:-1]

        if not url.endswith('.json'):
            url = url + '.json'

        try:
            jsons = self.db.get(url)
        except:
            self.send_error(404)
            return ""
            
        post = Post(**json.loads(jsons))
        post.db = self.db
        if post.author == self.current_user:
            post.delete()
            self.set_status(204)
        else:
            self.set_status(403)

#TODO: authorization -- always check the author of the updated object is equal to the current_user, see deleting and updating a post for example
