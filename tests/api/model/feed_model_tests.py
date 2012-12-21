import dustbin.config as config
import json
import urllib

from nose.tools import *
from dustbin.api.model import Author, Post, Feed
from dustbin.tests.helpers import *
from datetime import datetime as dt
from time import strftime

db = config.get_db()
author = create_author(db)
prefix = '/%s/private/facebook/posts' % author.subdomain


def setUp():
    db = config.get_db()
    db.open()
    author = create_author(db)

def tearDown():
    db.clear()
    db.close()


def test_add_post():
    f = Feed(url=prefix, author=author, db=db)
    assert len(f.entries) == 0
    f.add_post(Post('test this out', prefix = prefix, author=author))
    assert len(f.entries) == 1


def test_delete_post():
    f = Feed(title='facebook', url=prefix, author=author, db=db)
    p = Post('test this out', prefix = prefix, author=author)
    f.add_post(p)
    assert len(f.entries) == 1
    f.remove_post(p.url)
    assert len(f.entries) == 0
    assert_raises(Exception, f.remove_post, p.url)
    
    
#TODO: should be able to pass in an author as author in the feed constructor
def test_feed_json():
    now = dt.now()
    f = create_feed(now=now)
    p = Post('test this out\nright now')
    f.add_post(p)

    obj = json.loads(f.json)
    assert obj['title'] == 'pics'
    assert len(obj['links']) == 2
    assert obj['links'][0]['href'] == 'http://www.google.com'
    assert obj['updated'] == strftime('%Y-%m-%d %H:%M:%S', now.utctimetuple())
    assert len(obj['entries']) == 1
    entry = obj['entries'][0]
    assert entry.has_key('title')
    assert len(entry['title']) == 0
    assert entry['link'] == p.url
    assert entry['updated'] == strftime('%Y-%m-%d %H:%M:%S',
                                        p.date.utctimetuple())
    assert obj['author']['subdomain'] == 'potter'
    assert obj['author']['email'] == 'potter@motherfuckingsorcerer.com'


def test_author():
    f = create_feed()
    assert f.meta['author']['subdomain'] == 'potter'
    assert f.meta['author']['email'] == 'potter@motherfuckingsorcerer.com'


def test_load_from_db():
    '''
    Make sure we can save and rehydrate
    a feed instance from the database.
    '''
    f = create_feed()
    f.save(db=db)
    created = Feed(db=db).load(f.url)


def test_links():
    '''
    test that the links generated are correct.
                 links=[{'href' : 'http://www.google.com',
                       'rel' : 'self'},
                       {'href' : 'http://www.yahoo.com'}],

    '''
    f = Feed(title='facebook', url=prefix, author=author, db=db)
    assert len(f.links) == 2
    assert f.links[0]['rel'] == 'self'
    assert f.links[0]['href'] == 'http://www.%s%s' % (config.domain, f.url)
    assert f.links[1]['href'] == 'http://www.%s' % config.domain


def test_delete_feed():
    f = Feed(url=prefix, author=author, db=db)
    p = Post('test this out', prefix = prefix, author=author, db=db).save()
    f.add_post(p)
    f.delete()
    assert_raises(Exception, db.get, f.url)
    assert_raises(Exception, db.get, p.url)


def create_feed(now=None):
    author = Author(subdomain='potter',
                     email='potter@motherfuckingsorcerer.com')\
                     .save(db=db)
    if not now:
        now = dt.now()
    return Feed(title='pics',
             links=[{'href' : 'http://www.google.com',
                       'rel' : 'self'},
                       {'href' : 'http://www.yahoo.com'}],
            updated=now,
            author=author,
            url='/potter/private/pics/posts',
            db=db)

    

