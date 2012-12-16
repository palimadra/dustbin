import dustbin.config as config
import dustbin.tests.helpers as helpers
import tornado.web as web

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

    def test_post_urls(self):
        assert False

    def test_feed_urls(self):
        assert False
        
