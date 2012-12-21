import dustbin.config as config
import dustbin

from nose.tools import *
from dustbin.api.model import Author, Lense, Post
from dustbin.tests.helpers import *

db = config.get_db()

def setUp():
    db = config.get_db()
    db.open()

def tearDown():
    db.clear()
    db.close()

def test_add_author():
    a = Author(email='sean.fioritt@test.com',
                subdomain='sean')
    a.save(db=db)
    b = Author().load(a.url, db=db)
    assert a == b, "Author wasn't saved correctly"

    a = Author(db=db)
    assert_raises(Exception, a.save)

    a = Author(db=db, email='test')
    assert_raises(Exception, a.save)

    a = Author(db=db, subdomain='test')
    assert_raises(Exception, a.save)

    a = Author(db=db, email='test', subdomain='invalid subdomain')
    assert_raises(Exception, a.save)


def test_update_author():
    a = Author(db=db, email='test', subdomain='test')
    a.save()
    assert Author().load(a.url, db=db).email == 'test'
    
    a.email = 'changed'
    a.save()
    assert Author().load(a.url, db=db).email == 'changed'
    

def test_author_url():

    a = Author(email='test', subdomain='test')
    assert a.url == '/test'


def test_subdomain_validation():

    toolong = 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'
    badchars = 'dd-me'

    assert Author.valid_subdomain('good')
    assert not Author.valid_subdomain(toolong)
    assert not Author.valid_subdomain(badchars)

    #254 characters long
    domain = dustbin.config.domain
    dustbin.config.domain = 'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu'
    assert not Author.valid_subdomain('good'), 'Domain was too long, this should fail a validation check'
    dustbin.config.domain = domain


def test_delete_author():
    author = create_author(db)
    af = author.feed
    l = Lense(name = 'facebook',
              subdomain=SUBDOMAIN,
              db=db,
              author=author).save()

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

    author.delete()
    assert_raises(Exception, db.get, author.url)
    assert_raises(Exception, db.get, l.url)
    assert_raises(Exception, db.get, post.url)
    assert_raises(Exception, db.get, af.url)



def test_get_lenses():
    a = Author(email='sean.fioritt@test.com',
                subdomain='sean')
    a.save(db=db)
    assert len(a.lenses) == 0
    l = Lense(name = 'facebook',
              subdomain=SUBDOMAIN,
              db=db,
              author=a).save()
    a.update()
    assert len(a.lenses) == 1
    l.delete()
    a.update()
    assert len(a.lenses) == 0, "failed to delete lense"

