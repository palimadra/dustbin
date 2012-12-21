from nose.tools import *
from dustbin.api.model import Post, Lense
from datetime import datetime as dt
from dustbin.tests.helpers import *

import dustbin.config as config
import dustbin
import hashlib
import urllib
import json

db = config.get_db()
author = create_author(db)
prefix = '/sean/private/posts'

def setUp():
    db = config.get_db()
    db = config.get_db()
    author = create_author(db)
    db.open()

def tearDown():
    db.clear()
    db.close()

def test_post_url():

    content = 'this is a short post'
    ordinal = 734845
    date = dt.fromordinal(ordinal)
    post = Post(content, prefix='sean', date=date, author=author)
    expected = 'sean/12/8/2012/' + urllib.pathname2url(hashlib.sha256(content + post.meta['date']).digest())
    assert post.url == expected, 'url was  %s expected %s' % (post.url, expected)


def test_post_filename():

    content = 'some stuff in here'
    title = 'this is awesome'
    post = Post(content, prefix=prefix, author=author)
    expected = urllib.pathname2url(hashlib.sha256(content + post.meta['date']).digest())
    assert post.filename == expected, 'filename is %s expected %s' % (post.filename, expected)
    post = Post(content, prefix=prefix, title=title, author=author)
    assert post.filename == urllib.pathname2url(title.replace(' ', '-'))


def test_post_title():

    content = 'sweet content right here'
    title = 'awesome title'
    post = Post(content, prefix=prefix, author=author)
    assert post.title == ''
    post = Post(content, prefix=prefix, title=title, author=author)
    assert post.title == title


def test_post_save():
    '''
    saving a post should:
    1. update feeds (tested in feed test module)
    2. create a json entry at the url
    3. create an html fragment entry at the url.html
    '''
    content = 'check it'
    post = Post(content=content, prefix=prefix, db=db, author=author)
    post.save()
    newpost = Post(db=db).load(post.url + '.json')
    assert newpost == post
    assert post.fragment == db.get(post.url + '.html')
    
    

def test_post_json():
    '''
    Make sure json is in a format we expect.
    '''
    content = 'check it'
    post = Post(content=content,
                title='title here',
                author=author,
                prefix=prefix)
    meta = json.loads(post.json)
    for key, value in meta.items():
        assert post.meta[key] == value, 'meta value for %s was %s expected %s.' % (key, meta[key], value)
    

def test_load_from_db():
    '''
    Make sure we can save and rehydrate
    a post instance from the database.
    '''
    post = Post(content='test this out',
                title='super awesome title',
                author = author,
                prefix=prefix,
                db=db)
    post.save()
    saved = Post(db=db).load(post.url + '.json')
    assert saved == post


def test_bad_markdown():
    '''
    Make sure bad markup is removed.
    '''
    post = Post('<script>alert("evil!")</script><p>cool beans</p>',
                db=db)
    expected = '<p>alert("evil!")</p><p>cool beans</p><p></p>'
    assert post.fragment == expected, 'cleansed fragment was %s expected %s' % (post.fragment, expected)


def test_delete_post():

    tearDown()
    author = create_author(db)
    l = Lense(name = 'facebook',
              subdomain=SUBDOMAIN,
              db=db,
              author=author).save()

    assert len(l.feed.entries) == 0
    assert len(author.feed.entries) == 0
    
    post = Post(content='test this out',
                title='super awesome title',
                author = author,
                prefix=l.feed.url,
                db=db,
                lense=l).save()

    l.update()
    author.update()
    assert len(l.feed.entries) == 1
    assert len(author.feed.entries) == 1

    post.delete()
    l.update()
    author.update()
    assert len(l.feed.entries) == 0
    assert len(author.feed.entries) == 0
    

