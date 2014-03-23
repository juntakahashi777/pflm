import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import listing, listingmanager

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template(
            'Templates/homepage.html')
        self.response.write(template.render())

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/passes', listing.Passes),
    ('/latemeal', listing.LateMeal),
    ('/makelisting', listingmanager.MakeListing),
    ('/deletelisting', listingmanager.DeleteListing),
], debug=True)
