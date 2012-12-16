from nose.tools import *
from dustbin.api.model import Account, Post
from datetime import datetime as dt
from dustbin.tests.helpers import *

import dustbin.config as config
import dustbin
import hashlib
import urllib
import json

db = config.get_db()

def test_post_url():

    content = "this is a short post" 
    post = Post(content, prefix="sean")
    ordinal = 734845
    date = dt.fromordinal(ordinal)
    post.date = date
    expected = "sean/12/8/2012/" + urllib.pathname2url(hashlib.sha256(content + post.meta["date"]).digest())
    assert post.url == expected, "url was  %s expected %s" % (post.url, expected)


def test_post_filename():

    content = "some stuff in here"
    title = "this is awesome"
    post = Post(content)
    expected = urllib.pathname2url(hashlib.sha256(content + post.meta["date"]).digest())
    assert post.filename == expected, "filename is %s expected %s" % (post.filename, expected)
    post = Post(content, title=title)
    assert post.filename == urllib.pathname2url(title)


def test_post_title():

    content = "sweet content right here"
    title = "awesome title"
    post = Post(content)
    assert post.title == ""
    post = Post(content, title=title)
    assert post.title == title


def test_post_save():
    """
    saving a post should:
    1. update feeds (tested in feed test module)
    2. create a json entry at the url
    3. create an html fragment entry at the url.html
    """
    content = "check it"
    post = Post(content=content, db=db)
    post.save()
    newpost = Post(db=db).load(post.url + ".json")
    assert newpost == post
    assert post.fragment == db.get(post.url + ".html")
    
    

def test_post_json():
    """
    Make sure json is in a format we expect.
    """
    content = "check it"
    post = Post(content=content,
                title="title here")
    meta = json.loads(post.json)
    for key, value in meta.items():
        assert post.meta[key] == value, "meta value for %s was %s expected %s." % (key, meta[key], value)
    

def test_load_from_db():
    """
    Make sure we can save and rehydrate
    a post instance from the database.
    """
    post = Post(content="test this out",
                title="super awesome title",
                db=db)
    post.save()
    saved = Post(db=db).load(post.url + ".json")
    assert saved == post


def test_bad_markdown():
    """
    Make sure bad markup is removed.
    """
    post = Post("<script>alert('evil!')</script><p>cool beans</p>",
                db=db)
    expected = "<p>alert('evil!')</p><p>cool beans</p><p></p>"
    assert post.fragment == expected, "cleansed fragment was %s expected %s" % (post.fragment, expected)
