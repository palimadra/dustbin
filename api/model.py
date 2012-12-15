import dustbin.config as config
import json
import re
import dateutil.parser
import hashlib
import urllib
from datetime import datetime as dt


subdomainre = re.compile("^[a-zA-Z0-9]+$")

class Base:

    def __init__(self, meta=None):
        if meta:
            self.meta = meta
        else:
            self.meta = {}

    def __getattr__(self, name):
        if self.meta.has_key(name):
            return self.meta[name]
        else:
            raise AttributeError

    def __eq__(self, other):

        for key, value in self.meta.items():
            if other.meta[key] != value:
                return False
        return True
            

class Post(Base):

    def __init__(self,
                 content = "",
                 title = "",
                 date = None,
                 filename = ""):
        
        if not date:
            date = dt.now().isoformat()

        if not filename:
            filename = self.generate_filename(title, content)
            
        meta = {"title" : title,
                     "content" : content,
                     "date" : date,
                     "filename" : filename}

        Base.__init__(self, meta)


    @property
    def date(self):
        return dateutil.parser.parse(self.meta["date"])
    

    @date.setter
    def date(self, value):
        self.meta["date"] = value.toisoformat()


    @property
    def url(self):
        return "/".join([str(x) for x in
                   self.date.month,
                   self.date.day,
                   self.date.year,
                   self.filename])

    @property
    def json(self):
        return json.dumps(self.meta)

    def save(self):
        pass

    def generate_filename(self, title, content):
        if title:
            return urllib.pathname2url(title)
        else:
            hash = hashlib.sha256(content).digest()
            return urllib.pathname2url(hash)

        
class Account:

    def __init__(self, name, subdomain):

        self.name = name
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
