from nose.tools import *
from spyglass.api.model import Blog
import spyglass

def setup():
    pass

def test_subdomain_validation():

    toolong = "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    badchars = "dd-me"

    assert Blog.valid_subdomain("good")
    assert not Blog.valid_subdomain(toolong)
    assert not Blog.valid_subdomain(badchars)

    #254 characters long
    domain = spyglass.config.domain
    spyglass.config.domain = "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
    assert not Blog.valid_subdomain("good"), "Domain was too long, this should fail a validation check"
    spyglass.config.domain = domain


