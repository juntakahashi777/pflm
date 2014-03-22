import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2

clubs = ["cannon", "cap", "cottage","ivy", "ti", "tower"]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

''' Stores user requests for late meal/passes'''
class Listing(ndb.Model):
	date = ndb.DateTimeProperty(auto_now_add=True)
	netid = ndb.StringProperty(required=True)
	wantsPasses = ndb.BooleanProperty(required=True)
	club = ndb.StringProperty(choices=clubs, required=True)
	details = ndb.StringProperty(indexed=False)
	canceled = ndb.BooleanProperty(default=False)

class Passes(webapp2.RequestHandler):

	def get(self):
		listings_query = Listing.query(
			Listing.wantsPasses==True, Listing.canceled==False).order(-Listing.date)
		listings = listings_query.fetch(10)
		template_values = {'listings': listings}

		template = JINJA_ENVIRONMENT.get_template('Templates/passes.html')
		self.response.write(template.render(template_values))

class Latemeal(webapp2.RequestHandler):

	def get(self):
		template = JINJA_ENVIRONMENT.get_template('Templates/latemeal.html')
		self.response.write(template.render())
