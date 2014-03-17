import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def 

class User(ndb.Model):
    """Models an individual user with username, netid, etc."""
    userType = ndb.BooleanProperty()
    netid = ndb.StringProperty()
    details = ndb.StringProperty()
    requests = ndb.StructuredProperty(repeated=True)

    @classmethod
    def query_user(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)


class Request(ndb.Model):
    """Models a request made by a user."""
    time = ndb.DateTimeProperty()
    matchedId = ndb.StringProperty()
