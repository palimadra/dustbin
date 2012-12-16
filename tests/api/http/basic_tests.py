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
username = helpers.SUBDOMAIN

def setUp():
    db.set(helpers.EMAIL, helpers.SUBDOMAIN)
    db.open()

def tearDown():
    db.clear()
    db.close()


class BaseTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application()


    def create_post(self, url="/posts", post=None):
        if not post:
            post = model.Post("text is something like this.\nplus a paragraph",
                              title="title here",
                              prefix = helpers.url(url))
    
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        created = self.fetch(helpers.url(url),
                             method="POST",
                             body=post.json,
                             headers=headers)
        return post, created


class NewPostTest(BaseTest):
    
    def test_post(self):
        post, response = self.create_post()
        assert response.headers["Location"] == post.url,\
            "url was %s expected %s" % (response.headers["Location"], post.url)
        assert response.code == 201

    def test_post_to_lense(self):
        """
        If you post to a lense, make sure everything
        is created in the right spot in the database

        e.g. post /sean/posts/private/family
        versus post /sean/posts/public/computers
        """
        
        post, response = self.create_post(url="/posts/facebook")
        url = response.headers["Location"]
        assert url.startswith(helpers.url("/posts/facebook")), "post was created in the wrong place"
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.json
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "text/html"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment



class ReadPostTest(BaseTest):
    
    
    def test_get_json(self):

        post, created = self.create_post()
        url = created.headers["Location"]
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.json
        

    def test_get_html(self):
        
        post, created = self.create_post()
        url = created.headers["Location"]
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "text/html"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment



class FeedTest(BaseTest):

    def test_main_feed(self):
        tearDown()
        setUp()
        post, created = self.create_post()
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(helpers.url("/posts/feed"), headers=headers)
        feed = model.Feed()
        feed.add(post)
        assert feed.json == response.body


    def test_lense_feed(self):
        assert False
        
