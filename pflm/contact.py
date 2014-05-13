import webapp2, jinja2
import datetime, os
import listing
import CAS
import urllib, json
from google.appengine.api import urlfetch
import nameLookup

MANDRILL_URL = "https://mandrillapp.com/api/1.0/messages/send.json"

clubNames = {"cannon": "Cannon", "cap": "Cap", 
"cottage": "Cottage","ivy": "Ivy", "ti": "TI", "tower": "Tower"}

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

def getName(netid):
	netid.encode("ascii","ignore")
	if netid in nameLookup.lookup:
		return nameLookup.lookup[netid]
	return netid

class Contact(webapp2.RequestHandler):

	def post(self):
		netid = self.request.get("netid")
		listing_netid = self.request.get("listing_netid")


		listing_date = datetime.datetime.strptime(self.request.get("listing_date"),
			"%Y-%m-%d %H:%M:%S.%f")
		oldListing = listing.Listing.query(listing.Listing.netid == listing_netid,
			listing.Listing.date == listing_date)

		club = "" #to be filled in
		wantsPasses = True
		for l in oldListing:
			club = l.club
			wantsPasses = l.wantsPasses

			user_addresses =  [netid + '@princeton.edu', listing_netid + '@princeton.edu', 'utsarga.sikder@gmail.com']
			passWanter = ""
			passHaver = ""

			#names
			netid_name = getName(netid)
			listing_name = getName(listing_netid)
			if wantsPasses:
				passWanter = listing_name
				passHaver = netid_name
			else:
				passWanter = netid_name
				passHaver = listing_name

			sender_address = "PFLM Match <match@passesforlatemeal.com>"
			subject = "You made contact!"
			body = """<p>Hi %s and %s!</p>
				<p>We heard that %s wants to party at %s and %s wants to eat some late meal. You guys are in luck!</p>
				<p>Get in touch, grab some late meal (or get it delivered) and have a blast at %s!</p>
<p>Love,<br>The PassesForLateMeal Team</p><p><a href=www.passesforlatemeal.com><img align="left" src="http://www.passesforlatemeal.com/images/logo.png" height="30" width="auto"></a></p><br><br><p>---</p><p>%s, if you want to delete your request, you can do so at www.passesforlatemeal.com/myrequests.</p>""" % (listing_name, netid_name, passWanter, clubNames[club], passHaver, clubNames[club], listing_name)

			params = {
			"async": False,
			"message": {
			"from_name": "PassesForLateMeal Match",
			"track_opens": True,
			"html": body,
			"inline_css": False,
			"bcc_address": "match@passesforlatemeal.com",
			"from_email": "match@passesforlatemeal.com",
			"to": [
			   {
			       "type": "to",
			       "email": listing_netid+"@princeton.edu",
			       "name": listing_name
			   },
			   {
			       "type": "to",
			       "email": netid+"@princeton.edu",
			       "name": netid_name
			   },
			],
			"track_clicks": True,
			"subject": "Match on passesforlatemeal.com!"
			},
			"key": "K2Ymjia-FOcpVodZr8iRGA",
			}

			urlfetch.fetch(url=MANDRILL_URL, payload=json.dumps(params), 
				method=urlfetch.POST, headers={"Content-Type": "application/x-www-form-urlencoded"})
			template = JINJA_ENVIRONMENT.get_template('Templates/contacted.html')
			self.response.write(template.render())


