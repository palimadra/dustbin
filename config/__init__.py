#TODO: should read this from some config file
try:
    from prefs import *
except Exception as e:

    class DictWrapper:

        def __init__(self):
            self.dict = {}

        def get(self, key):
            return self.dict[key]

        def set(self, key, value):
            self.dict[key] = value

    domain = "test.com"

    def get_db():
        return DictWrapper()
