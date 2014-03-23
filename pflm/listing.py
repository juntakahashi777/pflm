import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2
import est, datetime

clubs = ["cannon", "cap", "cottage","ivy", "ti", "tower"]
clubNames = {"": "select club", "cannon": "Cannon", "cap": "Cap", 
"cottage": "Cottage","ivy": "Ivy", "ti": "TI", "tower": "Tower"}

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

'''Create a Datastore key for a Listing entity'''
def listing_key(wants="passes"):
	return ndb.Key('Listing', wants)

''' Given a datetime object, returns a pretty date for outputting '''
def prettyDate(date):
	estDate = date.replace(tzinfo=est.Eastern_tzinfo())
	estDate = estDate + estDate.tzinfo.utcoffset(estDate)
	ampm = "pm"
	if estDate.hour < 12:
		ampm = "am"
	hour = str(estDate.hour % 12)
	if hour == "0":
		hour = "12"
	minute = estDate.minute
	if minute < 10:
		minute = "0" + str(minute)
	prettyDate = str(estDate.month) + '/' + str(estDate.day) + " " + hour+ ":" + str(minute) + " " + ampm
	return prettyDate

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
		club = self.request.get('club')
		if club != '':
			listings_query = Listing.query(Listing.wantsPasses==True, 
				Listing.canceled==False, Listing.club==club,
				ancestor=listing_key("passes")).order(-Listing.date)
		else:
			listings_query = Listing.query(Listing.wantsPasses==True, 
				Listing.canceled==False,
				ancestor=listing_key("passes")).order(-Listing.date)

		prettyDates = []
		listings = listings_query.fetch(10)
		for utcListing in listings:
			prettyDates.append(prettyDate(utcListing.date))
		listings = zip(listings, prettyDates)

		template_values = {'listings': listings, 'club': clubNames[club]}

		template = JINJA_ENVIRONMENT.get_template("Templates/passes.html")
		self.response.write(template.render(template_values))

class LateMeal(webapp2.RequestHandler):

	def get(self):
		club = self.request.get('club')
		if club != '':
			listings_query = Listing.query(Listing.wantsPasses==False, 
				Listing.canceled==False, Listing.club==club,
				ancestor=listing_key("passes")).order(-Listing.date)
		else:
			listings_query = Listing.query(Listing.wantsPasses==False, 
				Listing.canceled==False,
				ancestor=listing_key("passes")).order(-Listing.date)

		prettyDates = []
		listings = listings_query.fetch(10)
		for utcListing in listings:
			prettyDates.append(prettyDate(utcListing.date))
		listings = zip(listings, prettyDates)
		
		template_values = {'listings': listings, 'club': clubNames[club]}

		template = JINJA_ENVIRONMENT.get_template("Templates/latemeal.html")
		self.response.write(template.render(template_values))
