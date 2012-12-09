import dustbin.api.model as model
import dustbin.tests.helpers as helpers
import tornado.web as web

from dustbin.api import Application
from nose.tools import *
from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders


class FeedTest(AsyncHTTPTestCase):
    
    def get_app(self):
        #return Application([('/', )])
        return Application()

    def test_post(self):
        post = model.Post("text is something like this.\nplus a paragraph", title="title")
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch("/sean/posts",
                   method="POST",
                   body=post.json,
                   headers=headers)
        
#        request = HTTPRequest('/sean/posts',
#                              method="POST",
#                              body=post.json,
#                              headers=HTTPHeaders({"Content-Type" : "application/json"}))
#        helpers.set_user_cookie(request)
#        response = self.http_client.fetch(request, self.stop)

        assert response.headers["Location"] == post.url
        assert response.code == 201
        
        

    


    




