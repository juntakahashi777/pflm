import webapp2, jinja2
import datetime, os
import listing
import CAS
from google.appengine.api import mail


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Contact(webapp2.RequestHandler):
	def post(self):
		netid = self.request.get("netid")
		listing_netid = self.request.get("listing_netid")


		listing_date = datetime.datetime.strptime(self.request.get("listing_date"),
			"%Y-%m-%d %H:%M:%S.%f")
		oldListing = listing.Listing.query(listing.Listing.netid == listing_netid,
			listing.Listing.date == listing_date)

		club = "" #to be filled in
		print oldListing
		for l in oldListing:
			club = l.club

		user_addresses =  [netid + '@princeton.edu', listing_netid + '@princeton.edu']
		sender_address = "PforLM Email <niharmadhavan@gmail.com>"
		subject = "You made contact!"
		body = """
		We heard you want to eat at %s. Well you're in luck! 
		Contact this fucker. go get late meal
		In the meantime, here's a dick 8===>
		""" % club

		mail.send_mail(sender_address, user_addresses, subject, body)

		template = JINJA_ENVIRONMENT.get_template('Templates/contacted.html')
		self.response.write(template.render())


