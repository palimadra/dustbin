from nose.tools import *
from dustbin.api.model import Account, Post
from datetime import datetime as dt

import dustbin
import hashlib
import urllib


def test_post_url():

    content = "this is a short post" 
    post = Post(content)
    #todo: date needs to be a property which accepts a datetime object and converts it
    # to isoformat which will be stored in the "raw" data of the post object and eventually
    # serialized and stored the database.
    ordinal = 734845
    date = dt.fromordinal(ordinal)
    post.date = date
    expected = "12/8/2012/" + urllib.pathname2url(hashlib.sha256(content).digest())
    assert post.url == expected, "url was  %s expected %s" % (post.url, expected)


def test_post_filename():

    content = "some stuff in here"
    title = "this is awesome"
    post = Post(content)
    expected = urllib.pathname2url(hashlib.sha256(content).digest())
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
    1. update feeds
    2. create a json entry at the url
    3. create an html fragment entry at the url.html
    """
    
    content = "check it"

