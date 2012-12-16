import dustbin.config as config
import dustbin.api.model as model
import dustbin.tests.helpers as helpers
import tornado.web as web

from nose.tools import *
from tornado.httputil import HTTPHeaders

db = config.get_db()
username = helpers.SUBDOMAIN

def setUp():
    db.set(helpers.EMAIL, helpers.SUBDOMAIN)
    db.open()

def tearDown():
    db.clear()
    db.close()



class NewPostTest(helpers.BaseTest):
    
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
        
        post, response = self.create_post(uri="/posts/facebook")
        url = response.headers["Location"]
        assert url.startswith(helpers.url("/posts/facebook")), "post was created in the wrong place"
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.json
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "text/html"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment


    def test_bad_content_type(self):
        assert False


class ReadPostTest(helpers.BaseTest):
    
    
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


class FeedTest(helpers.BaseTest):

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
        
