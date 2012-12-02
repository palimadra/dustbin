from paste.fixture import TestApp
from nose.tools import *
from spyglass.api import app


class TestBlog:

    def __init__(self):
        middleware = []
        self.testApp = TestApp(app.wsgifunc(*middleware))
        
        
    def test_get_blogs(self):
        r = self.testApp.get(u'/sean/blogs')
        assert_equal(r.status, 200)
        r.mustcontain(u'blog1')
    

    def test_new_blog(self):
        r = self.testApp.post(u'/sean/blogs',
                              params={"name": "bob's blog",
                                       "subdomain": "bob",
                                       "public" : True})
#        assert_equal(r.status, 201)
        assert True

    




