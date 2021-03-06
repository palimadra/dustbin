"""
Define a prefs.py file that defines
values below. Put it in the config folder.
"""

TAG_WHITELIST = ["div", "a", "p", "span", "h1", "h2", "h3", "blockquote", "ul", "li", "code", "pre"]
ATTR_WHITELIST = ["class", "id", "title", "src", "alt"]


try:
    from prefs import *
except Exception as e:

    class DictWrapper:
        """
        Defines the interface that must be implemented by
        the object returned by get_db. So any
        database can be used that implements this
        interface, and if it's not defined it
        gets stored in memory in a simple dictionary.
        """
        def __init__(self):
            self.dict = {}

        def get(self, key):
            return self.dict[key]

        def get_bulk(self, keys):
            return [self.dict[key] for key in keys]

        def set(self, key, value):
            self.dict[key] = value

        def remove(self, key):
            del self.dict[key]

        def open(self):
            pass

        def close(self):
            pass

        def clear(self):
            self.dict = {}


    #define these values in your prefs.py

    domain = "test.com"
    appsettings = dict(
            cookie_secret="some random number here.",
            autoescape=None
        )

    _db = DictWrapper()
    
    def get_db():
        return _db
