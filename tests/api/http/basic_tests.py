import dustbin.config as config
import dustbin.api.model as model
import dustbin.tests.helpers as helpers
import tornado.web as web
import json

from nose.tools import *
from tornado.httputil import HTTPHeaders

db = config.get_db()
username = helpers.SUBDOMAIN

def setUp():
    db.open()
    a = model.Account(subdomain=helpers.SUBDOMAIN, email=helpers.EMAIL)
    a.save(db=db)

def tearDown():
    db.clear()
    db.close()



class NewPostTest(helpers.BaseTest):
    
    def test_post(self):
        post, response = self.create_post(db=db)
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
        
        post, response = self.create_post(uri="/facebook/posts", db=db)
        url = response.headers["Location"]
        assert url.startswith(helpers.url("/facebook/posts")), "post was created in the wrong place"
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.json
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "text/html"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment


    def test_lense_named_posts(self):
        assert False


    def test_bad_content_type(self):
        post, created = self.create_post(db=db, contenttype="text/html")
        assert created.code == 500, "Only application/json should be supported for creating a post."



class ReadPostTest(helpers.BaseTest):
    
    
    def test_get_json(self):

        post, created = self.create_post(db=db)
        url = created.headers["Location"]
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.json
        

    def test_get_html(self):
        
        post, created = self.create_post(db=db)
        url = created.headers["Location"]
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "text/html"}))
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment


    def test_get_trailing_slash(self):
        """
        Make sure we handle requests for posts that have a trailing slash.
        """
        assert False


class FeedTest(helpers.BaseTest):

    def test_main_feed(self):
        tearDown()
        setUp()
        #TODO: posting, deleting or updating a post should update the lense
        # feed and the public/private feed.
        
        post, created = self.create_post(db=db)
        headers = helpers.set_user_cookie(HTTPHeaders({"Content-Type" : "application/json"}))
        response = self.fetch(helpers.url("/posts"), headers=headers)
        feed = model.Feed.get(helpers.url("/posts"), post.author, db)
        loaded = model.Feed(**json.loads(response.body))
        assert feed == loaded
        assert len(feed.entries) == 1

        #add another post
        post, created = self.create_post(db=db)
        response = self.fetch(helpers.url("/posts"), headers=headers)
        assert feed.json != response.body
        feed = model.Feed().load(helpers.url("/posts"), db=db)
        assert feed == model.Feed(**json.loads(response.body))


    def test_update_post(self):
        assert False


    def test_delete_post(self):
        assert False


    def test_lense_feed(self):
        assert False
        

class AccountTest(helpers.BaseTest):

    def test_existing_account(self):
        """
        make sure an existing account can't be overriden.
        """
        assert False
