import web
import model
import json

urls = (
    '/(.*)/blogs', 'Blogs',
)


class Blogs:

    form = web.form.Form(
        web.form.Textbox('name', web.form.notnull, 
            size=140,
            description="Blog name"),
            
        web.form.Textbox('subdomain', web.form.notnull, 
            size=63,
            description="Subdomain for the blog"),

        web.form.Checkbox('public', 
            description="Public or private"),
            
        web.form.Button('Create new blog'),
    )
    

    def GET(self, name):
        """
        Return the list of blogs this person owns.
        """
        web.header('Content-Type', 'application/json')
        blogs = model.get_blogs(name)
        return json.dumps(blogs)



    def POST(self, name):
        """
        Start a new blog.
        """
        form = self.form()

        if form.validates():
            blog = model.new_blog(form.d.name,
                                  form.d.public,
                                  form.d.subdomain)
            web.ctx.status = '201 Created'
            web.header('Location', blog.url)
            web.header('Content-Type', 'text/html')
            return ""
        else:
            #TODO: more useful error message
            raise web.internalerror(message="Something went wrong.")


app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()


