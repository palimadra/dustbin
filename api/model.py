

def get_blogs(name):

    """
    Returns some meta data about the blogs for the
    given name.
    1. The title of the blog
    2. The url of the blog
    """

    return ["blog1", "blog2", name]


def new_blog(name, public):

    pass


class Blog:

    def __init__(self, name, public):

        self.name = name
        self.public = public

    @property
    def url(self):
        return 
