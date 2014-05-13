import webapp2
import datetime
import listing
import CAS
import contact

class MakeListing(webapp2.RequestHandler):

	def post(self):
		netid = self.request.get("netid")

		wantsPasses = self.request.get("wantsPasses")
		if wantsPasses == "True":
			wantsPasses = True
		else:
			wantsPasses = False
		club = self.request.get("club")
		details = self.request.get("details")

		nickname = self.request.get("nickname")
		print nickname

		if club != "select":
			newListing = listing.Listing(parent=listing.listing_key())
			newListing.populate(netid=netid, wantsPasses=wantsPasses,
				club=club.lower(), details=details, nickname=nickname)
			newListing.put()
		if wantsPasses:
			self.redirect("/passes?requested=%s" % club)
		else:
			self.redirect("/latemeal?requested=latemeal")

class DeleteListing(webapp2.RequestHandler):

	def post(self):
		listing_netid = self.request.get("listing_netid")
		redirect_url = self.request.get("redirect_url")
		print redirect_url
		listing_date = datetime.datetime.strptime(self.request.get("listing_date"),
			"%Y-%m-%d %H:%M:%S.%f")
		oldListing = listing.Listing.query(listing.Listing.netid == listing_netid,
			listing.Listing.date == listing_date)
		for l in oldListing:
			l.canceled = True
			l.put()
		self.redirect(redirect_url)

class DeleteAll(webapp2.RequestHandler):

	def post(self):
		listing_netid = self.request.get("listing_netid")
		listings = listing.Listing.query(listing.Listing.netid == listing_netid,
			listing.Listing.canceled==False)
		for l in listings:
			l.canceled = True
			l.put()
		self.redirect("/myrequests")
