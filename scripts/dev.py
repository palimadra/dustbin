import tornado
from tornado.options import define, options
import dustbin

define("port", default=8888, help="run on the given port", type=int)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(dustbin.api.Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
