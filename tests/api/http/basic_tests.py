import dustbin.config as config
import dustbin.api.model as model
import dustbin.tests.helpers as helpers
import tornado.web as web

from dustbin.api import Application
from nose.tools import *
from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders

db = config.get_db()

def setUp():
    db.set(helpers.EMAIL, helpers.SUBDOMAIN)
    db.open()

def tearDown():
    db.clear()
    db.close()


class FeedTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return Application()


    def blah_test_post(self):
        post = model.Post("text is something like this.\nplus a paragraph", title="title")
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(helpers.url("/posts"),
                   method="POST",
                   body=post.json,
                   headers=headers)
        
        assert response.headers["Location"] == post.url
        assert response.code == 201
        
        

    


    




