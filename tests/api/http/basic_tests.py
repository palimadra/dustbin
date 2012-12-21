import dustbin.config as config
import dustbin.api.model as model
import tornado.web as web
import json

from dustbin.tests.helpers import *
from nose.tools import *
from tornado.httputil import HTTPHeaders

db = config.get_db()
author = create_author(db)
username = SUBDOMAIN

def setUp():
    db = config.get_db()
    db.open()
    author = create_author(db)
    author.save(db=db)

def tearDown():
    db.clear()
    db.close()



class NewPostTest(BaseTest):
    
    def test_post(self):
        post, response = self.create_post(db=db)
        assert response.headers['Location'] == post.url,\
            'url was %s expected %s' % (response.headers['Location'], post.url)
        assert response.code == 201

    def test_post_to_lense(self):
        '''
        If you post to a lense, make sure everything
        is created in the right spot in the database

        e.g. post /sean/posts/private/family
        versus post /sean/posts/public/computers
        '''
        
        post, response = self.create_post(uri='/facebook/posts', db=db, author=author)
        location = response.headers['Location']
        assert location.startswith(url('/facebook/posts')), 'post was created in the wrong place'
        headers = set_user_cookie(contenttype='application/json', author=author)
        response = self.fetch(location, headers=headers)
        assert response.body == post.json
        headers = set_user_cookie(author=author)
        response = self.fetch(location, headers=headers)
        assert response.body == post.fragment


    def test_bad_content_type(self):
        post, created = self.create_post(db=db, contenttype='text/html')
        assert created.code == 500, 'Only application/json should be supported for creating a post.'



class ReadPostTest(BaseTest):
    
    
    def test_get_json(self):

        post, created = self.create_post(db=db)
        url = created.headers['Location']
        headers = set_user_cookie(contenttype='application/json')
        response = self.fetch(url, headers=headers)
        assert response.body == post.json
        

    def test_get_html(self):
        
        post, created = self.create_post(db=db)
        url = created.headers['Location']
        headers = set_user_cookie()
        response = self.fetch(url, headers=headers)
        assert response.body == post.fragment


    def test_get_trailing_slash(self):
        '''
        Make sure we handle requests for posts that have a trailing slash.
        '''
        post, created = self.create_post(db=db)
        url = created.headers['Location']
        headers = set_user_cookie()
        response = self.fetch(url + '/', headers=headers)
        assert response.body == post.fragment, 'Post urls should support trailing slash'


class FeedTest(BaseTest):

    def test_main_feed(self):
        tearDown()
        setUp()
        #TODO: posting, deleting or updating a post should update the lense
        # feed and the public/private feed.
        
        post, created = self.create_post(db=db)
        headers = set_user_cookie(contenttype='application/json')
        response = self.fetch(url('/posts'), headers=headers)
        feed = model.Feed.get(url('/posts'), post.author, db)
        loaded = model.Feed(**json.loads(response.body))
        assert feed == loaded
        assert len(feed.entries) == 1

        #add another post
        post, created = self.create_post(db=db)
        response = self.fetch(url('/posts'), headers=headers)
        assert feed.json != response.body
        feed = model.Feed().load(url('/posts'), db=db)
        assert feed == model.Feed(**json.loads(response.body))


    def test_update_post(self):
        post, created = self.create_post(db=db, author=author)
        post.content = "new content"
        headers = set_user_cookie(contenttype="application/json", author=author)
        response = self.fetch(post.url,
                             method='PUT',
                             body=post.json,
                             headers=headers)
        assert response.code == 204
        response = self.fetch(post.url, headers=headers)
        assert post.json == response.body


    def test_delete_post(self):
        post, created = self.create_post(db=db, author=author)
        headers = set_user_cookie(author=author)
        response = self.fetch(post.url,
                             method='DELETE',
                             headers=headers)
        assert response.code == 204
        response = self.fetch(post.url + ".json", headers=headers)
        assert response.code == 404
        response = self.fetch(post.url + ".html", headers=headers)
        assert response.code == 404
        response = self.fetch(post.url, headers=headers)
        assert response.code == 404


    def test_lense_feed(self):
        post, created = self.create_post(db=db, author=author)
        headers = set_user_cookie(contenttype='application/json', author=author)
        response = self.fetch(post.prefix, headers=headers)
        feed = model.Feed.get(post.prefix, post.author, db)
        loaded = model.Feed(**json.loads(response.body))
        assert feed == loaded
        assert len(feed.entries) == 1
        author.feed.update()
        assert len(author.feed.entries) == 1


        #add another post
        post, created = self.create_post(db=db)
        response = self.fetch(post.prefix, headers=headers)
        assert feed.json != response.body
        feed = model.Feed().load(post.prefix, db=db)
        assert feed == model.Feed(**json.loads(response.body))
        author.feed.update()
        assert len(author.feed.entries) == 2

        

class AuthorTest(BaseTest):

    def test_existing_author(self):
        '''
        make sure an existing author can't be overriden.
        '''
        assert False

#TODO: make sure posting to just a /subdomain/public/ url has a feed at /subdomain/public/posts
