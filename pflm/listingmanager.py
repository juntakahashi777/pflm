import webapp2
import datetime
import listing
import CAS

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
			self.redirect("/passes")
		else:
			self.redirect("/latemeal")

class DeleteListing(webapp2.RequestHandler):

	def post(self):
		listing_netid = self.request.get("listing_netid")
		print self.request.get("listing_date")
		listing_date = datetime.datetime.strptime(self.request.get("listing_date"),
			"%Y-%m-%d %H:%M:%S.%f")
		oldListing = listing.Listing.query(listing.Listing.netid == listing_netid,
			listing.Listing.date == listing_date)
		wantsPasses = True
		for l in oldListing:
			l.canceled=True
			l.put()
			wantsPasses = l.wantsPasses
		if wantsPasses:
			self.redirect("/passes")
		else:
			self.redirect('latemeal')
