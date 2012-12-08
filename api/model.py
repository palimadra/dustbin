import spyglass.config as config
import spyglass.db.orm as orm
import re


subdomainre = re.compile("^[a-zA-Z0-9]+$")

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
