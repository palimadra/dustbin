from nose.tools import *
from dustbin.api.model import Account
import dustbin

def setup():
    pass

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


