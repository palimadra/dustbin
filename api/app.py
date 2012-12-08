import pykt
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
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/test", TestHandler)
        ]
        settings = dict(
            cookie_secret="^gh\x06t\x08\xd8m2\x01\xf83\xfeu\xd3\xa9I\xcc6\x8d",
            login_url="/auth/login",
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = pykt.KyotoTycoon()
        self.db.open()


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


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):

        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        email = user["email"].encode("utf-8")
        name = self.db.get(email)
        if not name:
            name = user["name"].encode("utf-8")
            self.db.set(email, name)

        self.set_secure_cookie("user", email)
        self.redirect(self.get_argument("next", "/"))


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()



