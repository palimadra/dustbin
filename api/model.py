import spyglass.config as config
import re

subdomainre = re.compile("^[a-zA-Z0-9]+$")

def get_blogs(name):

    """
    Returns some meta data about the blogs for the
    given name.
    1. The title of the blog
    2. The url of the blog
    """

    return ["blog1", "blog2", name]


def new_blog(name, subdomain, public):

    """
    Create a new blog. Persist it in
    the database.
    """
    if Blog.valid_subdomain(subdomain):
        return Blog(name, subdomain, public)
    else:
        raise Exception("The subdomain was invalid")
    

class Blog:

    def __init__(self, name, subdomain, public):

        self.name = name
        self.public = public
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
