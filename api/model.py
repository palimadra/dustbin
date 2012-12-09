import dustbin.config as config
import re
import dateutil.parser
import sha
import urllib
from datetime import datetime as dt


subdomainre = re.compile("^[a-zA-Z0-9]+$")


class Post:

    def __init__(self, content, title=None):
        self.content = content
        self.title = title
        self.meta = {}
        self.meta["date"] = dt.now().isoformat()

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
    def filename(self):
        if self.title:
            return urllib.pathname2url(self.title) + ".html"
        else:
            return sha.sha(self.content).digest() + ".html"

        
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
