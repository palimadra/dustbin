from paste.fixture import TestApp
from nose.tools import *
from spyglass.api import app
from spyglass.api.model import new_blog

class TestBlog:

    def __init__(self):
        middleware = []
        self.testApp = TestApp(app.wsgifunc(*middleware))
        
        
    def test_get_blogs(self):
        r = self.testApp.get(u'/sean/blogs')
        assert_equal(r.status, 200)
        r.mustcontain(u'blog1')
    

    def test_new_blog(self):
        name = "bob's blog"
        subdomain = "bob"
        public = True

        blog = new_blog(name, subdomain, public)
        r = self.testApp.post(u'/sean/blogs',
                              params={"name": name,
                                       "subdomain": subdomain,
                                       "public" : public})

        
        assert_equal(r.status, 201)
        assert_equal(blog.url, dict(r.headers)["Location"])

    




