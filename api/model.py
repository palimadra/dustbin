import dustbin.config as config
import json
import re
import dateutil.parser
import sha
import urllib
from datetime import datetime as dt


subdomainre = re.compile("^[a-zA-Z0-9]+$")


class Post:

    def __init__(self,
                 content = "",
                 title = "",
                 date = None):
        
        self.content = content
        self.title = title

        if not date:
            date = dt.now().isoformat()
            
        self.meta = {"title" : title,
                     "content" : content,
                     "date" : date}
        
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

    @property
    def json(self):
        return json.dumps(self.meta)

        
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
