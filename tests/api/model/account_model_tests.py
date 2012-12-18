import dustbin.config as config
import dustbin

from nose.tools import *
from dustbin.api.model import Account
from dustbin.tests.helpers import *

db = config.get_db()

def test_add_account():
    a = Account(email="sean.fioritt@test.com",
                subdomain="sean")
    a.save(db=db)
    b = Account().load(a.url, db=db)
    assert a == b, "Account wasn't saved correctly"

    a = Account(db=db)
    assert_raises(Exception, a.save)

    a = Account(db=db, email="test")
    assert_raises(Exception, a.save)

    a = Account(db=db, subdomain="test")
    assert_raises(Exception, a.save)

    a = Account(db=db, email="test", subdomain="invalid subdomain")
    assert_raises(Exception, a.save)


def test_delete_account():
    assert False
    
def test_update_account():
    a = Account(db=db, email="test", subdomain="test")
    a.save()
    assert Account().load(a.url, db=db).email == "test"
    
    a.email = "changed"
    a.save()
    assert Account().load(a.url, db=db).email == "changed"
    

def test_account_url():

    a = Account(email="test", subdomain="test")
    assert a.url == "/test"


def test_subdomain_validation():

    toolong = "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    badchars = "dd-me"

    assert Account.valid_subdomain("good")
    assert not Account.valid_subdomain(toolong)
    assert not Account.valid_subdomain(badchars)

    #254 characters long
    domain = dustbin.config.domain
    dustbin.config.domain = "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
    assert not Account.valid_subdomain("good"), "Domain was too long, this should fail a validation check"
    dustbin.config.domain = domain


