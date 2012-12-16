import dustbin.config as config
import json

from nose.tools import *
from dustbin.api.model import Account, Post, Feed
from dustbin.tests.helpers import *
from datetime import datetime as dt

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
    
    
#TODO: should be able to pass in an account as author in the feed constructor
def test_feed_json():
    now = dt.now()
    f = Feed(title="test",
             links=[{"href" : "http://www.google.com",
                       "rel" : "self"},
                       {"href" : "http://www.yahoo.com"}],
            updated = now,
            author = {"name" : "harry",
                       "email" : "potter@motherfuckingsorcerer.com"})
    
    p = Post("test this out\nright now")
    f.add_post(p)

    obj = json.loads(f.json)
    assert obj["title"] == "test"
    assert len(obj["links"]) == 2
    assert obj["links"][0]["href"] == "http://www.google.com"
    assert obj["updated"] == strftime("%Y-%m-%d %H:%M:%S", now.utctimetuple())
    assert len(obj["entries"]) == 1
    entry = obj["entries"][0]
    assert not entry.has_key("title")
    assert entry["link"] == p.url
    assert entry["updated"] == strftime("%Y-%m-%d %H:%M:%S",
                                        p.date.utctimetuple())
    assert entry["author"]["name"] == "harry"
    assert entry["author"]["email"] == "potter@motherfuckingsorcerer.com"


def test_feed_save():
    assert False
    

def test_load_from_db():
    """
    Make sure we can save and rehydrate
    a feed instance from the database.
    """
    assert False
