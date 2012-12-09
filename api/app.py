import dustbin.config as config
import json
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/([^/]+)/private/posts", PostsHandler)
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


class PostsHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self, subdomain):
        self.request.body
