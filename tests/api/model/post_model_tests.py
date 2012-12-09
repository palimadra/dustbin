from nose.tools import *
from dustbin.api.model import Account, Post
from datetime import datetime as dt

import dustbin
import sha
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
    assert post.url == "12/8/2012/" + sha.sha(content).digest() + ".html", "oops, url was actually %s" % post.url


def test_post_filename():

    content = "some stuff in here"
    title = "this is awesome"
    post = Post(content)
    assert post.filename == sha.sha(content).digest() + ".html"
    post = Post(content, title=title)
    assert post.filename == urllib.pathname2url(title) + ".html"


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
    1. update the feed
    2. create a json entry at the url
    3. create an html fragment entry at the url.html
    """
    
    content = "check it"

