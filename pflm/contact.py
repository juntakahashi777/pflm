import webapp2, jinja2
import datetime, os
import listing
import CAS
import urllib, json
from google.appengine.api import urlfetch

MANDRILL_URL = "https://mandrillapp.com/api/1.0/messages/send.json"

clubNames = {"cannon": "Cannon", "cap": "Cap", 
"cottage": "Cottage","ivy": "Ivy", "ti": "TI", "tower": "Tower"}

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

def getName(netid):
	url = 'http://www.princeton.edu/main/tools/search/index.xml?q='+netid
	f = urllib.urlopen(url)
	html = f.read()
	soup = BeautifulSoup(html)
	soup = soup.find("div", {"id": "search-people-results"})
	for person in soup.find_all("li"):
		attributes = person.find_all("a")
		if attributes[1].get_text().split()[0].lower() == netid.lower()+u"@princeton.edu":
			return attributes[0].get_text().split(',')[1].split()[0]

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
			if wantsPasses:
				passWanter = netid
				passHaver = listing_netid
			else:
				passWanter = listing_netid
				passHaver = netid

			sender_address = "PFLM Match <match@passesforlatemeal.com>"
			subject = "You made contact!"
			body = ""
			if wantsPasses:
				body = """<p>Hi!</p>
				<p>We heard that %s wants to party at %s and %s wants to eat some late meal. You guys are in luck!</p>
				<p>Get in touch, go get some late meal (or get it delivered) and go wild at %s!</p>
<p>Love,<br>PassesForLateMeal</p><br><p>---</p><p>%s, if you want to delete your request, you can do so at www.passesforlatemeal.com/myrequests.</p>""" % (passWanter, clubNames[club], passHaver, clubNames[club], passHaver)

			params = {
			"async": False,
			"message": {
			"from_name": "PassesForLateMeal Match",
			"track_opens": True,
			"html": body,
			"inline_css": False,
			"bcc_address": "message.bcc_address@example.com",
			"from_email": "match@passesforlatemeal.com",
			"to": [
			   {
			       "type": "to",
			       "email": listing_netid+"@princeton.edu"
			   },
			   {
			       "type": "to",
			       "email": netid+"@princeton.edu",
			   },
			],
			"track_clicks": True,
			"subject": "Match on passesforlatemeal!"
			},
			"key": "CP0ZcMEThOjYt4UwbVkE1w",
			}

			urlfetch.fetch(url=MANDRILL_URL, payload=json.dumps(params), 
				method=urlfetch.POST, headers={"Content-Type": "application/x-www-form-urlencoded"})
			template = JINJA_ENVIRONMENT.get_template('Templates/contacted.html')
			self.response.write(template.render())


