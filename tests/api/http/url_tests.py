import dustbin.config as config
import dustbin.tests.helpers as helpers
import tornado.web as web
import re

from dustbin.api import Application, urlpatterns
from nose.tools import *

db = config.get_db()
username = helpers.SUBDOMAIN

def setUp():
    db.set(helpers.EMAIL, helpers.SUBDOMAIN)
    db.open()

def tearDown():
    db.clear()
    db.close()


class UrlTests(helpers.BaseTest):

    def test_new_post_urls(self):
        reg = re.compile(urlpatterns["NewPostHandler"])
        assert reg.match("/sean/private/posts")
        assert reg.match("/sean/private/posts/")
        assert reg.match("/sean/private/facebook/posts")
        assert reg.match("/sean/private/facebook/posts/")
        assert reg.match("/sean/public/posts")
        assert reg.match("/sean/public/posts/")
        assert reg.match("/sean/public/facebook/posts")
        assert reg.match("/sean/public/facebook/posts/")
        
        assert not reg.match("/sean/private/facebook/posts/bam")
        assert not reg.match("/sean/private/facebook/posts/bam/")
        assert not reg.match("/sean/private/facebook/posts/11/12/2012")
        assert not reg.match("/sean/private/facebook/11")
        assert not reg.match("/sean/public/facebook/posts/bam")
        assert not reg.match("/sean/public/facebook/posts/bam/")
        assert not reg.match("/sean/public/facebook/posts/11/12/2012")
        assert not reg.match("/sean/")
        assert not reg.match("/sean/public")
        assert not reg.match("/sean/public/pos")
        assert not reg.match("/sean/public/posts/11/12/2014")

    def test_post_urls(self):
        assert False
        
    def test_feed_urls(self):
        reg = re.compile(urlpatterns["FeedsHandler"])
        assert reg.match("/sean/private/feed")
        assert reg.match("/sean/private/feed.json")
        assert reg.match("/sean/private/facebook/feed")
        assert reg.match("/sean/public/facebook/feed.json")

        assert not reg.match("/sean/public/feed.dust")
        assert not reg.match("/sean/private/test/this/feed")
        assert not reg.match("/sean/public/test/this/feed.json")
        
