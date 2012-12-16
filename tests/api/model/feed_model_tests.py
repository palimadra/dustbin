from nose.tools import *
from dustbin.api.model import Account, Post, Feed
from dustbin.tests.helpers import *

import dustbin.config as config

db = config.get_db()


def test_add_post():
    f = Feed("test")
    assert len(f.entries) == 0
    f.add_post(Post("test this out"))
    assert len(f.entries) == 1


def test_delete_post():
    f = Feed("test")
    p = Post("test this out")
    f.add_post(p)
    assert len(f.entries) == 1
    f.remove_post(p.url)
    assert len(f.entries) == 0
    assert_raises(Exception, f.remove_post, p.url)
    

def test_feed_json():
    assert False


def test_feed_save():
    """
    """
    assert False
    

def test_load_from_db():
    """
    Make sure we can save and rehydrate
    a feed instance from the database.
    """
    assert False
