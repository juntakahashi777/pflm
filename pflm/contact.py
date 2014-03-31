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
		wantsPasses = True
		for l in oldListing:
			club = l.club
			wantsPasses = l.wantsPasses

		user_addresses =  [netid + '@princeton.edu', listing_netid + '@princeton.edu', 'utsarga.sikder@gmail.com']
		sender_address = "PFLM Match <match@passesforlatemeal.com>"
		subject = "You made contact!"
		body = ""
		if wantsPasses:
			body = """
Hi!

We heard that %s wants to party at %s and %s wants to eat some late meal. Well, you guys are in luck! Get in touch, go get some late meal and go wild at %s! If you're feeling up for it, drop us an email about how it all went. Send us a story, a picture--whatever you want!

%s, if you want to delete your request, you can do so at passesforlatemeal.com/myrequests. In the meantime, enjoy your passes and late meal!

Love,
passesforlatemeal
""" % (listing_netid, club, netid, club, listing_netid)
		else:
			body = body = """
Hi!

We heard that %s wants to party at %s and %s wants to eat some late meal. Well, you guys are in luck! Get in touch, go get some late meal and go wild at %s! If you're feeling up for it, drop us an email about how it all went. Send us a story, a picture--whatever you want!

%s, if you want to delete your request, you can do so at passesforlatemeal.com/myrequests. In the meantime, enjoy your passes and late meal!

Love,
passesforlatemeal
""" % (netid, club, listing_netid, club, listing_netid)
		mail.send_mail(sender_address, user_addresses, subject, body)

		template = JINJA_ENVIRONMENT.get_template('Templates/contacted.html')
		self.response.write(template.render())


