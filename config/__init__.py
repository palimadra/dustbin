#TODO: should read this from some config file
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

        def set(self, key, value):
            self.dict[key] = value

        def open(self):
            pass

        def close(self):
            pass

        def clear(self):
            self.dict = {}

    domain = "test.com"
    appsettings = dict(
            cookie_secret="some random number here.",
            autoescape=None
        )

    def get_db():
        return DictWrapper()
