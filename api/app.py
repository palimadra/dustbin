import web
import model
import json

urls = (
    '/(.*)/blogs', 'Blogs',
)


class Blogs:

    def GET(self, name):
        web.header('Content-Type', 'application/json')
        blogs = model.get_blogs(name)
        return json.dumps(blogs)


app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()


