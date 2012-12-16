import dustbin.config as config
import json
import re
import dateutil.parser
import hashlib
import urllib
import os.path as path

from bleach import clean
from markdown2 import markdown
from datetime import datetime as dt


subdomainre = re.compile("^[a-zA-Z0-9]+$")

class Base:

    def __init__(self, db=None, meta=None):
        if meta:
            self.meta = meta
        else:
            self.meta = {}

        self.db = db

    def __getattr__(self, name):
        if self.meta.has_key(name):
            return self.meta[name]
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name in ['db', 'meta']:
            self.__dict__[name] = value
        else:
            self.__dict__['meta'][name] = value

    def __eq__(self, other):

        for key, value in self.meta.items():
            if other.meta[key] != value:
                return False
        return True

    def load(self, key):
        assert self.db, "No db instance. Provide a db instance when creating the model"
        self.meta = json.loads(self.db.get(key))
        return self
            

class Post(Base):

    def __init__(self,
                 content="",
                 prefix="",
                 title = "",
                 date = None,
                 filename = "",
                 db=None):
        
        if not date:
            date = dt.now().isoformat()

        if not filename:
            filename = self.generate_filename(title, content)
            
        meta = {"title" : title,
                     "content" : content,
                     "date" : date,
                     "filename" : filename,
                     "prefix" : prefix}

        Base.__init__(self, db=db, meta=meta)


    @property
    def date(self):
        return dateutil.parser.parse(self.meta["date"])
    

    @date.setter
    def date(self, value):
        self.meta["date"] = value.toisoformat()


    @property
    def url(self):
        return path.join(*([self.prefix] + [str(x) for x in
                                        self.date.month,
                                        self.date.day,
                                        self.date.year,
                                        self.filename]))

    @property
    def json(self):
        return json.dumps(self.meta)


    @property
    def fragment(self):
        return clean(markdown(self.content),
                     tags=config.TAG_WHITELIST,
                     attributes=config.ATTR_WHITELIST,
                     strip=True)


    def save(self, db=None):
        if db:
            self.db = db
        assert self.db, "You must provide a db instance to the model constructor to save."
        self.db.set(self.url, self.json)
        self.db.set(self.url + ".html", self.fragment)


    def generate_filename(self, title, content):
        if title:
            return urllib.pathname2url(title)
        else:
            hash = hashlib.sha256(content).digest()
            return urllib.pathname2url(hash)

        
class Account:

    def __init__(self, email, subdomain):

        self.email = email
        self.subdomain = subdomain


    @staticmethod
    def valid_subdomain(subdomain):

        if len(subdomain) > 63:
            return False
        
        elif len(config.domain) + len(subdomain) > 255:
            return False
        
        elif not subdomainre.match(subdomain):
            return False
        
        else:
            return True

    @property
    def url(self):
        return self.subdomain + "." + config.domain


class Feed(Base):

    def __init__(self, post):
        Base.__init__(self)

    @property
    def json(self):
        return ""
