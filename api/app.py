import dustbin.config as config
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/test", TestHandler)
        ]
        settings = dict(
            cookie_secret="^gh\x06t\x08\xd8m2\x01\xf83\xfeu\xd3\xa9I\xcc6\x8d",
            autoescape=None
        )
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


class HomeHandler(BaseHandler):
    def get(self):
        self.write("blah")

class TestHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("blah")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()



