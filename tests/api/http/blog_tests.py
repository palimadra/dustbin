from paste.fixture import TestApp
from nose.tools import *
from spyglass.api import app


def setup():
    pass


def test_get_blogs():
    middleware = []
    testApp = TestApp(app.wsgifunc(*middleware))
    r = testApp.get(u'/sean/blogs')
    assert_equal(r.status, 200)
    r.mustcontain(u'blog1')




