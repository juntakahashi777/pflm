import urllib
import CASClient
import os

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


netid = ""

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


DEFAULT_GUESTBOOK_NAME = 'passes'


# We set a parent key on the 'requests' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with author, details, and date."""
    details = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
## adding these fields
    userType = ndb.BooleanProperty()
    netid = ndb.StringProperty()
    club = ndb.StringProperty()
    details = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):


    def get(self):

        C = CASClient.CASClient()
        global netid 
        netid = C.Authenticate(self)

        # Ancestor Queries, as shown here, are strongly consistent with the High
        # Replication Datastore. Queries that span entity groups are eventually
        # consistent. If we omitted the ancestor from this query there would be
        # a slight chance that Greeting that had just been written would not
        # show up in a query.
        requests_query = Greeting.query(
            ancestor=guestbook_key(DEFAULT_GUESTBOOK_NAME)).order(-Greeting.date)
        requests = requests_query.fetch(20)


        template_values = {
            'requests': requests,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class HomePage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('homepage.html')
        self.response.write(template.render())

class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(DEFAULT_GUESTBOOK_NAME))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        ## adding code here

        greeting.userType = True
        greeting.netid = netid
        greeting.club = self.request.get('club')

        ## added

        greeting.details = self.request.get('details')
        greeting.put()

        query_params = {'guestbook_name': DEFAULT_GUESTBOOK_NAME}
        self.redirect('/?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/homepage', HomePage),
], debug=True)