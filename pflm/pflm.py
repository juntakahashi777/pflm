import os
import urllib
import cgi, urlparse
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import listing, listingmanager, contact

import CAS

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

class MainPage(webapp2.RequestHandler):

    def get(self):
        CAS.CAS(self)
        template = JINJA_ENVIRONMENT.get_template(
            'Templates/homepage.html')
        self.response.write(template.render())

class AboutUs(webapp2.RequestHandler):

    def get(self):
        CAS.CAS(self)
        template = JINJA_ENVIRONMENT.get_template(
            'Templates/about.html')
        self.response.write(template.render())

class About2(webapp2.RequestHandler):

    def get(self):
        CAS.CAS(self)
        template = JINJA_ENVIRONMENT.get_template(
            'Templates/about2.html')
        self.response.write(template.render())

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/about', AboutUs),
    ('/about2', About2),
    ('/passes', listing.Passes),
    ('/latemeal', listing.LateMeal),
    ('/myrequests', listing.MyRequests),
    ('/contact', contact.Contact),
    ('/makelisting', listingmanager.MakeListing),
    ('/deletelisting', listingmanager.DeleteListing),
    ('/deleteall', listingmanager.DeleteAll),
], debug=True)
