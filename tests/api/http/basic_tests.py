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


class NewPostTest(AsyncHTTPTestCase):
    
    def get_app(self):
        return Application()


    def test_post(self):
        post = model.Post("text is something like this.\nplus a paragraph",
                          title="title",
                          prefix=helpers.url("/posts"))
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(helpers.url("/posts"),
                   method="POST",
                   body=post.json,
                   headers=headers)
        
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
        
        assert False


class ReadPostTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application()
    
    def test_get_json(self):

        post = model.Post("text is something like this.\nplus a paragraph",
                          title="title here",
                          prefix = helpers.url("/posts"))
        
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        created = self.fetch(helpers.url("/posts"),
                              method="POST",
                              body=post.json,
                              headers=headers)

        url = created.headers["Location"]
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.json

    def test_get_html(self):
        post = model.Post("text is something like this.\nplus a paragraph",
                          title="title here",
                          prefix = helpers.url("/posts"))
        
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        created = self.fetch(helpers.url("/posts"),
                              method="POST",
                              body=post.json,
                              headers=headers)

        url = created.headers["Location"]
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "text/html"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment

