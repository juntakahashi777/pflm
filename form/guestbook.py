import cgi
import urllib
import CASClient


from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2


MAIN_PAGE_FORM_TEMPLATE = """\
    <form action="/sign" method="post">
      I want passes from 
    <select name="club">
    <option value="cap">Cap</option>
    <option value="cottage">Cottage</option>
    <option value="ivy">Ivy</option>
    <option value="ti">TI</option>
    <option value="tower">Tower</option>
    </select></div>
      details
      <div><textarea name="details" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Submit Request"></div>
    </form>
    <hr>
    """

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <hr>
  </body>
</html>
"""


DEFAULT_GUESTBOOK_NAME = 'passes'


# We set a parent key on the 'Greetings' to ensure that they are all in the same
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


        self.response.write('<html><body>')

        # Write the submission form and the footer of the page
        self.response.write(MAIN_PAGE_FORM_TEMPLATE)

        # Ancestor Queries, as shown here, are strongly consistent with the High
        # Replication Datastore. Queries that span entity groups are eventually
        # consistent. If we omitted the ancestor from this query there would be
        # a slight chance that Greeting that had just been written would not
        # show up in a query.
        greetings_query = Greeting.query(
            ancestor=guestbook_key(DEFAULT_GUESTBOOK_NAME)).order(-Greeting.date)
        greetings = greetings_query.fetch(3)

        for greeting in greetings:

            print greeting

            self.response.write('<b>club</b>: %s\n </br>' %greeting.club)
            self.response.write('<i>netid</i>: %s\n </br>' % greeting.netid)
            self.response.write('<i>details</i>: %s\n </br>' % greeting.details)
            self.response.write('<i>usertype</i>: %s\n </br>' %greeting.userType)
            self.response.write('<i>date</i>: %s\n </br>' %greeting.date)
            self.response.write('</br>')

        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE)


class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(DEFAULT_GUESTBOOK_NAME))


        greeting.userType = True
        greeting.netid = netid
        greeting.club = self.request.get('club')

        greeting.details = self.request.get('details')
        greeting.put()

        query_params = {'guestbook_name': DEFAULT_GUESTBOOK_NAME}
        self.redirect('/?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)