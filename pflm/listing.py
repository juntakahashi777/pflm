import os
import urllib
import CAS
from google.appengine.ext import ndb

import jinja2
import webapp2
import est, datetime

import random

MAX_LISTINGS = 5

clubNames = {"cannon": "Cannon", "cap": "Cap", 
"cottage": "Cottage","ivy": "Ivy", "ti": "TI", "tower": "Tower"}
filterNames = {"cannon": "Cannon", "cap": "Cap", 
"cottage": "Cottage","ivy": "Ivy", "ti": "TI", "tower": "Tower","latemeal": "Late Meal"}

# 20 character max
pass_seeker_nicknames = [
"ThirstyUnderclassman", 
"PumpedForProspect", 
"LookingForPasses", 
"CluelessFreshman",
"ProspectiveBickeree",
"5.95ForLife",
"PassHunter",
"PuffPuffPass",
"BackThatPassUp",
"PasstMyPrime",
"PassedOut",
"PassasaurusRex",
"Passtronomer",
"Passtrophysics",
"Passtroboy",
"PassMeTheFries",
"MentionedinPassing",
"PassLikeThat",
"SpongebobPasspants",
"CampusClubMember",
"PasstramiSandwich",
"PassTense",
"pASSpASSpASS",
"Passablanca",
]

# 20 character max
lm_seeker_nicknames = [
"HungryUpperclassman", 
"IWantChickenFingers", 
"QuesadillaIsAGoodIdea",
"LateNightPizzaLover",
"LateMealisRealMeal",
"Domingo",
"ChillUpperclassman",
"PassDaddy",
"SurrenderTheTenders",
"EyesOnTheFries",
"PassDaddy",
"StressedOutSenior",
"LouisPassteur",
"JustPassingThrough",
"PassauSt",
"Passtafarian",
"Passafist",
"Passtor",
"PassStation",
"BarackPassbama",
"PassahamLincoln",
"GeorgePassington",
"NorthwestPassage",
"Passagawea",
"Passover",
"Sepasstion",
"PassionOfTheChrist",
"Passcal",
]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

'''Create a Datastore key for a Listing entity'''
def listing_key(key="pflm"):
	return ndb.Key('Listing', key)

''' Given a datetime object, returns a pretty date for outputting '''
def prettyDate(date):
	weekdays = {0:"Monday",1:"Tuesday",2:"Wednesday",
	3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
	today = datetime.datetime.today()
	estToday = today.replace(tzinfo=est.Eastern_tzinfo())
	estToday += estToday.tzinfo.utcoffset(estToday)
	estDate = date.replace(tzinfo=est.Eastern_tzinfo())
	estDate += estDate.tzinfo.utcoffset(estDate)
	print estToday, estDate
	date = ""
	if estToday.date() == estDate.date():
		date = "Today"
	elif estToday.date() == estDate.date() + datetime.timedelta(days=1):
		date = "Yesterday"
	elif estToday.date() < estDate.date() + datetime.timedelta(days=7):
		date = weekdays[estDate.weekday()]
	else:
		date = str(estDate.month) + '/' + str(estDate.day)
	ampm = "PM"
	if estDate.hour < 12:
		ampm = "AM"
	hour = str(estDate.hour % 12)
	if hour == "0":
		hour = "12"
	minute = estDate.minute
	if minute < 10:
		minute = "0" + str(minute)
	prettyDate = date + ", " + hour+ ":" + str(minute) + " " + ampm
	return prettyDate

''' Stores user requests for late meal/passes'''
class Listing(ndb.Model):
	date = ndb.DateTimeProperty(auto_now_add=True)
	netid = ndb.StringProperty(required=True)
	nickname = ndb.StringProperty(required=True)
	wantsPasses = ndb.BooleanProperty(required=True)
	club = ndb.StringProperty(choices=clubNames.keys(), required=True)
	details = ndb.StringProperty(indexed=False, default="")
	canceled = ndb.BooleanProperty(default=False)

''' Returns three most recent results and 7 random other ones '''
def curtailListings(listings):
	RECENT_COUNT = 3
	RANDOM_COUNT = 7
	results = []
	i = 0
	for listing in listings:
		results.append(listing)
	results = results[:RECENT_COUNT]+random.sample(results[RECENT_COUNT:], 
		min(len(results[RECENT_COUNT:]), RANDOM_COUNT))
	results.sort(key=lambda l: l.date)
	results.reverse()
	return results

def getResultsMessage(wantsFilter, hasFilter):
	if wantsFilter=="cap" and hasFilter=="cap":
		return "Cap passes for Cap passes? No one's that chill"
	if wantsFilter=="latemeal" and hasFilter=="latemeal":
		return "Yo dawg I heard you like Late Meal"
	if wantsFilter=="tower" and hasFilter=="tower":
		return "This might not be the right tool for that"
	return ""

class Passes(webapp2.RequestHandler):

	def get(self):
		netid = CAS.CAS(self)
		if type(netid) != type(u""):
			return
		canPost = False

		MAX_LISTINGS = 6
		userListings = Listing.query(Listing.netid == netid, 
			Listing.canceled==False)
		numListings = 0
		for userListing in userListings:
			numListings+=1
		if numListings < MAX_LISTINGS:
			canPost = True

		listings = []
		wantsFilter = ''
		wantsText = 'anything'
		wants = self.request.get('wants')
		if wants in clubNames or wants == "latemeal":
			wantsFilter = wants
			wantsText = filterNames[wants]
		hasFilter = ''
		hasText = 'anything'
		has = self.request.get('has')
		if has in clubNames or has == "latemeal":
			hasFilter = has
			hasText = filterNames[has]

		if wantsFilter in clubNames and hasFilter not in clubNames:
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==True, Listing.club==wantsFilter,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter not in clubNames and hasFilter in clubNames:
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==False, Listing.club==hasFilter,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter == "latemeal" and hasFilter != "latemeal":
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==False,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter != "latemeal" and hasFilter == "latemeal":
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==True,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter == "" and hasFilter == "":
			listings_query = Listing.query(Listing.canceled==False, ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		prettyDates = []
		for utcListing in listings:
			prettyDates.append(prettyDate(utcListing.date))
		listings = zip(listings, prettyDates)

		resultsFound = True
		if len(prettyDates) == 0:
			resultsFound = False
		#generate nickname
		random_number = random.randint(1,99)
		nickname = random.choice(pass_seeker_nicknames) + str(random_number)

		resultsMessage = getResultsMessage(wantsFilter, hasFilter)
		template_values = {'listings': listings, 'netid': netid, 
		'clubs': clubNames, 'nickname': nickname, 'canPost': canPost, 'wants': wantsFilter, 'has': hasFilter,
		'wantsText': wantsText, 'hasText': hasText, 'resultsMessage': resultsMessage}

		template = JINJA_ENVIRONMENT.get_template("Templates/passes.html")
		self.response.write(template.render(template_values))


class LateMeal(webapp2.RequestHandler):

	def get(self):
		netid = CAS.CAS(self)
		if type(netid) != type(u""):
			return
		canPost = False

		MAX_LISTINGS = 6
		userListings = Listing.query(Listing.netid == netid, 
			Listing.canceled==False)
		numListings = 0
		for userListing in userListings:
			numListings+=1
		if numListings < MAX_LISTINGS:
			canPost = True

		listings = []
		wantsFilter = ''
		wantsText = 'anything'
		wants = self.request.get('wants')
		if wants in clubNames or wants == "latemeal":
			wantsFilter = wants
			wantsText = filterNames[wants]
		hasFilter = ''
		hasText = 'anything else'
		has = self.request.get('has')
		if has in clubNames or has == "latemeal":
			hasFilter = has
			hasText = filterNames[has]

		if wantsFilter in clubNames and hasFilter not in clubNames:
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==True, Listing.club==wantsFilter,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter not in clubNames and hasFilter in clubNames:
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==False, Listing.club==hasFilter,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter == "latemeal" and hasFilter != "latemeal":
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==False,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter != "latemeal" and hasFilter == "latemeal":
			listings_query = Listing.query(Listing.canceled==False, Listing.wantsPasses==True,
				ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		elif wantsFilter == "" and hasFilter == "":
			listings_query = Listing.query(Listing.canceled==False, ancestor=listing_key("pflm")).order(-Listing.date)
			listings = curtailListings(listings_query)
		prettyDates = []
		for utcListing in listings:
			prettyDates.append(prettyDate(utcListing.date))
		listings = zip(listings, prettyDates)
		resultsFound = True
		if len(prettyDates) == 0:
			resultsFound = False
		#generate nickname
		random_number = random.randint(1,99)
		nickname = random.choice(lm_seeker_nicknames) + str(random_number)

		template_values = {'listings': listings, 'netid': netid, 
		'clubs': clubNames, 'nickname': nickname, 'canPost': canPost, 'wants': wantsFilter, 'has': hasFilter,
		'wantsText': wantsText, 'hasText': hasText, 'resultsFound': resultsFound}

		template = JINJA_ENVIRONMENT.get_template("Templates/latemeal.html")
		self.response.write(template.render(template_values))

class MyRequests(webapp2.RequestHandler):
	def get(self):
		netid = CAS.CAS(self)
		if type(netid) != type(u""):
			return
		myRequests = Listing.query(Listing.netid == netid, 
			Listing.canceled==False, ancestor=listing_key("pflm")).order(-Listing.date)

		prettyDates = []
		for utcListing in myRequests:
			prettyDates.append(prettyDate(utcListing.date))
		myRequests = zip(myRequests, prettyDates)

		template_values = {'listings': myRequests, 'netid': netid, 'clubs': clubNames, }
		template = JINJA_ENVIRONMENT.get_template("Templates/myrequests.html")
		self.response.write(template.render(template_values))
