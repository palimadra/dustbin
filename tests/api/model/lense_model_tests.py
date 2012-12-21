import dustbin.config as config
import json

from nose.tools import *
from dustbin.api.model import Lense, Feed, Post
from dustbin.tests.helpers import *

db = config.get_db()

def setUp():
    db = config.get_db()
    db.open()

def tearDown():
    db.clear()
    db.close()


def test_create_lense():
    
    author = create_author(db)
    l = Lense(name = 'facebook',
              subdomain=SUBDOMAIN,
              db=db,
              author=author).save()
    loaded = Lense().load(l.url, db=db)
    assert loaded == l
    return l
    

def test_delete_lense():
    lense = test_create_lense()
    a = lense.author
    f = lense.feed
    assert Feed().load(f.url, db) == f
    lense.delete()
    assert_raises(Exception, db.get, f.url)
    assert_raises(Exception, db.get, lense.url)
    
def test_lense_json():
    lense = test_create_lense()
    jsons = lense.json
    fromjson = Lense(**json.loads(jsons))
    assert fromjson == lense

def test_lense_feed():
    lense = test_create_lense()
    feed = lense.feed
    f = Feed().load(feed.url, db=db)
    assert f == feed
    assert f.url == lense.url + "/posts"


def test_lense_url():
    l = Lense(name = 'facebook',
              subdomain=SUBDOMAIN,
              db=db,
              author=create_author(db))
    assert l.url == "/%s/%s/%s" % (SUBDOMAIN, 'public', 'facebook')
    l = Lense(name = 'facebookistan',
              subdomain=SUBDOMAIN,
              db=db,
              public=False,
              author=create_author(db))
    assert l.url == "/%s/%s/%s" % (SUBDOMAIN, 'private', 'facebookistan')


    
def test_name_is_posts():
    #shouldn't be able to name it posts
    author = create_author(db)
    l = Lense(name = 'posts',
              subdomain=SUBDOMAIN,
              db=db,
              author=author)
    assert_raises(AssertionError, l.save)

def test_new_post_updates():
    #creating a new post updates lense
    #feed and author feed
    lense = test_create_lense()
    assert len(lense.feed.entries) == 0
    assert len(lense.author.feed.entries) == 0
    post = Post('test this shit out',
                prefix='/sean/public/%s/posts' % lense.name,
                author=lense.author,
                lense=lense)
    post.save(db=db)
    lense.update()
    assert len(lense.feed.entries) == 1
    assert len(lense.author.feed.entries) == 1
    post.delete()
    lense.update()
    assert len(lense.feed.entries) == 0
    assert len(lense.author.feed.entries) == 0


def test_create_lense_same_name():

    author = create_author(db)
    l = Lense(name='facebook',
              subdomain=SUBDOMAIN,
              db=db,
              author=author)
    l.save()
    l = Lense(name='facebook',
              subdomain=SUBDOMAIN,
              db=db,
              public=False,
              author=author)
    assert_raises(AssertionError, l.save)

    

