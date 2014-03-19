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

DEFAULT_LISTINGS_DIRECTORY = 'passes'


# We set a parent key on the 'requests' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def listing_key(listing_name=DEFAULT_LISTINGS_DIRECTORY):
    """Constructs a Datastore key for a Listings entity with listing_name."""
    return ndb.Key('Listings', listing_name)


class Greeting(ndb.Model):
    """Models an individual Listings entry with author, details, and date."""
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
            ancestor=listing_key(DEFAULT_LISTINGS_DIRECTORY)).order(-Greeting.date)
        requests = requests_query.fetch(20)

        template_values = {
            'requests': requests,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Listings(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        listing_name = self.request.get('listing_name',
                                          DEFAULT_LISTINGS_DIRECTORY)
        request = Greeting(parent=listing_key(DEFAULT_LISTINGS_DIRECTORY))

        if users.get_current_user():
            request.author = users.get_current_user()

        ## adding code here

        request.userType = True
        request.netid = netid
        request.club = self.request.get('club')
        ## Need to add code to make sure there is a club selected

        request.details = self.request.get('details')
        ## Need to add code to clean input
        request_key = request.put()

        query_params = {'listing_name': DEFAULT_LISTINGS_DIRECTORY}
        self.redirect('/?' + urllib.urlencode(query_params))

class DeletePost(webapp2.RequestHandler):

    def post(self):
        key = ndb.Key(Listings, self.request.get("name"))
        key.delete()

        requests_query = Greeting.query(
            ancestor=listing_key(DEFAULT_LISTINGS_DIRECTORY)).order(-Greeting.date)
        requests = requests_query.fetch(20)

        template_values = {
            'requests': requests,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Listings),
    ('/delete', DeletePost)
], debug=True)