import dustbin.config as config
import json
import urllib

from nose.tools import *
from dustbin.api.model import Account, Post, Feed
from dustbin.tests.helpers import *
from datetime import datetime as dt
from time import strftime

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
    f = create_feed(now=now)
    p = Post("test this out\nright now")
    f.add_post(p)

    obj = json.loads(f.json)
    assert obj["title"] == "test"
    assert len(obj["links"]) == 2
    assert obj["links"][0]["href"] == "http://www.google.com"
    assert obj["updated"] == strftime("%Y-%m-%d %H:%M:%S", now.utctimetuple())
    assert len(obj["entries"]) == 1
    entry = obj["entries"][0]
    assert entry.has_key("title")
    assert len(entry['title']) == 0
    assert entry["link"] == p.url
    assert entry["updated"] == strftime("%Y-%m-%d %H:%M:%S",
                                        p.date.utctimetuple())
    assert obj["author"]["name"] == "harry"
    assert obj["author"]["email"] == "potter@motherfuckingsorcerer.com"


def test_author():
    f = create_feed()
    assert f.meta["author"]["name"] == "harry"
    assert f.meta["author"]["email"] == "potter@motherfuckingsorcerer.com"


def test_load_from_db():
    """
    Make sure we can save and rehydrate
    a feed instance from the database.
    """
    f = create_feed()
    f.save(db=db)
    created = Feed(db=db).load(f.url + ".json")


def test_feed_url():
    title = "facebook sucks"
    f = Feed(title, prefix="sean")
    escaped = urllib.pathname2url(title.replace(" ", "-"))
    expect = "sean/" + escaped
    assert f.url == expect, "url was %s expected %s" % (f.url, expect)
    f = Feed(prefix="sean/public/posts")
    expect = "sean/public/posts/feed"
    assert f.url == expect, "url was %s expected %s" % (f.url, expect)


def create_feed(now=None):
    author = Account(subdomain="harry",
                     email="potter@motherfuckingsorcerer.com")\
                     .save(db=db)
    if not now:
        now = dt.now()
    return Feed(title="test",
             links=[{"href" : "http://www.google.com",
                       "rel" : "self"},
                       {"href" : "http://www.yahoo.com"}],
            updated=now,
            author=author)

