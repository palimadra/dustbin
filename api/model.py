import dustbin.config as config
import json
import re
import cgi
import dateutil.parser
import hashlib
import urllib
import os.path as path
import types

from bleach import clean
from markdown2 import markdown
from datetime import datetime as dt
from time import strftime
from urls import urlpatterns

subdomainre = re.compile('^[a-zA-Z0-9]+$')

class Base(object):

    '''
    This is basically a lightweight orm for a key value store. Everything
    in the meta property is serialized and stored in the key/value store
    as json. A model can also be rehydrated using just a string of json.

    Define what attributes your model supports by defining keyword
    arguments in the __init__ function. Those will be automatically
    added to the meta dictionary and then persisted in the database.
    
    If you want to override an attribute, create a property and that
    property will be called instead, just be sure to set the value
    you eventually want to persist on the meta object, e.g.:
    
    class Human(Base):

       def __init__(self, name='', job=''):
          if not job:
             job = 'programmer'
          assert name, "you must have a name to be human"
          Base.__init__(self, **locals())

       @property
       def name(self):
          print 'do something here if you want'
          return self.meta['name']

       @name.setter
       def name(self, value):
          print 'do something here if you want'
          self.meta['name'] = value
    
    '''
    
    def __init__(*args, **kwargs):

        # delete self so we don't try to set it later
        if kwargs.has_key('self'):
            del kwargs['self']

        if len(args) >= 1:
            self = args[0]
        else:
            raise TypeError('You must pass in "self" to the init method')

        self.meta = {}

        # Every model contains a reference to the
        # db object. But it's only required to eventually
        # persist to the database. Db is not stored in
        # the meta object, so we have to explicitly set
        # it here.
        if kwargs.has_key('db'):
            self.db = kwargs['db']
        else:
            self.db = None
            
        for key, value in kwargs.items():
            self.__setattr__(key, value)


    def __getattr__(self, name):
        '''
        If a property isn't defined on the super class we
        look in the meta object instead of on the base
        class.
        '''
        if self.meta.has_key(name):
            return self.meta[name]
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        #meta and db never go into the meta property
        if hasattr(type(self), name) or name in ['meta', 'db']:
            object.__setattr__(self, name, value)
        else:
            self.meta[name] = value

    def __eq__(self, other):

        for key, value in self.meta.items():
            if other.meta[key] != value:
                return False
        return True


    def update(self):
        '''
        Refresh the object from the database
        '''
        self.load(self.url)


    def delete(self, db=None):
        if db:
            self.db = db
        self.db.remove(self.url)
        

    def load(self, key, db=None):
        if db:
            self.db = db
        assert self.db, 'No db instance. Provide a db instance when creating the model or as a keyword to this method'
        self.meta = json.loads(self.db.get(key))
        return self


    @property
    def url(self):
        return self.meta['url']

    @url.setter
    def url(self, value):
        self.meta['url'] = value

    @property
    def json(self):
        return json.dumps(self.meta)

    @property
    def author(self):
        url = Author.get_url(self.meta['author']['subdomain'])
        return Author(db=self.db).load(url)

    @author.setter
    def author(self, author):

        if author and type(author) == Author:
            self.meta['author'] = {'subdomain' : author.subdomain,
                                   'email' : author.email}

        # this is a dictionary format.
        elif author:
            self.meta['author'] = author
            
        else:
            self.meta['author'] = None


class Lense(Base):

    def __init__(self,
                 name='',
                 subdomain = '',
                 feed=None,
                 public=True,
                 db=None,
                 author=None):
        '''
        Lenses are used to separate content by reader.
        So you can create a lense called 'family' and then
        only allow family members to read it.

        Lenses have a feed that keeps track of posts.
        '''
        Base.__init__(self, **locals())

    @property
    def feed(self):
        return Feed.get(self.meta['feed'], self.author, self.db)

    @feed.setter
    def feed(self, feed):
        if type(feed) == types.UnicodeType:
            self.meta['feed'] = feed
        elif type(feed) == Feed:
            self.meta['feed'] = feed.url

    @property
    def url(self):
        pubpriv = 'public'
        if not self.public:
            pubpriv = 'private'
            
        return '/%s/%s/%s' % (self.subdomain, pubpriv, self.name)


    def save(self, db=None):
        if db:
            self.db = db
        assert self.db, 'You must provide a db instance to the model constructor to save.'
        assert self.name != 'posts', "A lense can't be named 'posts'."
        assert self.name not in [lense.name for lense in self.author.lenses]
        self.feed = Feed.get(self.url + '/posts', self.author, self.db).save()
        self.db.set(self.url, self.json)
        self.author.add_lense(self)
        return self
        

    def delete(self, db=None):
        if db:
            self.db = db
        self.feed.delete()
        self.author.remove_lense(self)
        self.db.remove(self.url)


            
class Post(Base):

    def __init__(self,
                 content='',
                 prefix='',
                 title = '',
                 date = None,
                 filename = '',
                 db=None,
                 author = None,
                 lense = None):
        
        if not date:
            date = dt.now()

        if not filename:
            filename = self.generate_filename(title, content, date.isoformat())

        Base.__init__(self, **locals())


    @property
    def lense(self):
        if self.meta.has_key('lense'):
            return Lense(db=self.db).load(self.meta['lense'])
        else:
            return None

    @lense.setter
    def lense(self, lense):
        if type(lense) == types.UnicodeType:
            self.meta['lense'] = lense
        elif type(lense) == Lense:
            self.meta['lense'] = lense.url
    

    @property
    def date(self):
        return dateutil.parser.parse(self.meta['date'])
    

    @date.setter
    def date(self, value):
        if type(value) == types.UnicodeType:
            self.meta['date'] = value
        else:
            self.meta['date'] = value.isoformat()

        if hasattr(self, 'filename'):
            self.filename = self.generate_filename(self.title, self.content, self.meta['date'])


    @property
    def url(self):
        return path.join(*([self.prefix] + [str(x) for x in
                                        self.date.month,
                                        self.date.day,
                                        self.date.year,
                                        self.filename]))

    @property
    def fragment(self):
        return clean(markdown(self.content),
                     tags=config.TAG_WHITELIST,
                     attributes=config.ATTR_WHITELIST,
                     strip=True)


    def save(self, db=None):
        if db:
            self.db = db
        assert self.db, 'You must provide a db instance to the model constructor to save.'
        self.db.set(self.url + '.json', self.json)
        self.db.set(self.url + '.html', self.fragment)
        feed = Feed.get(self.prefix, self.author, self.db)
        feed.add_post(self)
        self.author.feed.add_post(self)
        return self


    def delete(self, db=None):
        if db:
            self.db = db
        assert self.db, 'You must provide a db instance to the model constructor to save.'
        feed = Feed.get(self.prefix, self.author, self.db)
        feed.remove_post(self)
        self.author.feed.remove_post(self)
        self.db.remove(self.url + '.json')
        self.db.remove(self.url + '.html')



    def generate_filename(self, title, content, date):
        if title:
            title = title.replace(' ', '-')
            return urllib.pathname2url(title)
        else:
            hash = hashlib.sha256(content + date).digest()
            return urllib.pathname2url(hash)

        
class Author(Base):

    def __init__(self,
                 db=None,
                 email=None,
                 subdomain=None,
                 feed=None,
                 lenses=None):

        if not lenses:
            lenses = []

        Base.__init__(self, **locals())
        

    def save(self, db=None):
        if db:
            self.db = db
        assert self.db, 'You must provide a db instance to the model constructor to save.'
        assert self.email, 'email is required'
        assert self.subdomain, 'subdomain is required'
        assert Author.valid_subdomain(self.subdomain), 'Subdomain is invalid'

        #TODO: always save to the url without .json extension as a default, only add json extension
        # if there are multiple representation possibilities.
        feed = Feed.get('/%s/feed' % self.subdomain, self, self.db)
        self.feed = feed
        self.db.set(self.url, self.json)
        
        #this must come after saving the author model,
        #otherwise it fails when trying to access the author model.
        feed.save() 
        return self

    def delete(self, db=None):
        
        if db:
            self.db = db
            
        for lense in self.lenses:
            lense.delete(db=self.db)

        self.feed.delete(db=self.db)
        self.db.remove(self.url)
            

    def add_lense(self, lense):
        assert lense.url not in [lense.url for lense in self.lenses]
        self.lenses = [lense.url] + self.meta['lenses']
        self.save()


    def remove_lense(self, lense):
        if type(lense) == Lense:
            id = lense.url
        else:
            id = lense
        
        if id in [lense.url for lense in self.lenses]:
            self.lenses = [lense.url for lense in self.lenses if lense.url != id]
            self.save()
        else:
            raise Exception('Lense not found')


    #TODO: this pattern is so common, factor it out.
    @property
    def feed(self):
        return Feed.get(self.meta['feed'], self, self.db)

    @feed.setter
    def feed(self, feed):
        if type(feed) == types.UnicodeType:
            self.meta['feed'] = feed
        elif type(feed) == Feed:
            self.meta['feed'] = feed.url

    @property
    def lenses(self):
        return [Lense(**json.loads(jsons)) for jsons in self.db.get_bulk(self.meta['lenses'])]

    @lenses.setter
    def lenses(self, lenses):
        self.meta['lenses'] = lenses

    @property
    def url(self):
        return Author.get_url(self.subdomain)


    @staticmethod
    def get_url(subdomain):
        return '/' + subdomain


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


class Feed(Base):

    def __init__(self,
                 title=None,
                 url='',
                 db=None,
                 links=None,
                 updated=None,
                 author=None,
                 entries=None):

        if not entries:
            entries = []

        if not links:
            links = [{'href' : 'http://www.%s%s' % (config.domain, url),
                       'rel' : 'self'},
                     {'href' : 'http://www.%s' % config.domain}]

        if not updated:
            updated = dt.now()

        if not title:
            title = 'feed'

        Base.__init__(self, **locals())


    def add_post(self, post):
        entry = {}
        entry['content'] = cgi.escape(post.fragment)
        entry['id'] = post.url
        entry['title'] = post.title
        entry['link'] = post.url
        entry['updated'] =  strftime('%Y-%m-%d %H:%M:%S', post.date.utctimetuple())
        self.entries = [entry] + self.entries
        self.save()


    def remove_post(self, post):
        if type(post) == Post:
            id = post.url
        else:
            id = post
        
        if id in [entry['id'] for entry in self.entries]:
            self.entries = [entry for entry in self.entries if entry['id'] != id]
            self.save()
        else:
            raise Exception('Post not found')


    @property
    def updated(self):
        return dateutil.parser.parse(self.meta['updated'])
    

    @updated.setter
    def updated(self, value):
        if type(value) == types.UnicodeType:
            self.meta['updated'] = value
        else:
            self.meta['updated'] = strftime('%Y-%m-%d %H:%M:%S', value.utctimetuple())


    def save(self, db=None):
        if db:
            self.db = db
        assert self.url.startswith('/' + self.author.subdomain), "url %s doesn't start with subdomain of author: %s" % (self.url, self.author.subdomain)
        assert self.db, 'You must provide a db instance to the model constructor to save.'
        assert self.title, 'Feeds require a title.'
        assert self.url.endswith('/posts') or self.url.endswith('/feed')
        self.db.set(self.url, self.json)
        return self


    @staticmethod
    def get(url, author, db):
        try:
            feed = Feed(db=db).load(url)
        except:
            pattern = re.compile(urlpatterns['FeedHandler'])
            groups = pattern.match(url)
            title = groups.groupdict()['subdomain']
            feed = Feed(db=db,
                        url=url,
                        author=author,
                        title=title)
        return feed


