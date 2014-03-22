import webapp2
import datetime
import listing

class MakeListing(webapp2.RequestHandler):

	def post(self):
		netid = "jun"
		wantsPasses = self.request.get("wantsPasses")
		print wantsPasses
		if wantsPasses == "True":
			wantsPasses = True
		else:
			wantsPasses = False
		club = self.request.get("club")
		details = self.request.get("details")

		if club:
			newListing = listing.Listing()
			newListing.populate(netid=netid, wantsPasses=wantsPasses,
				club=club, details=details)
			newListing.put()
			self.redirect("/")
		elif wantsPasses:
			self.redirect("/passes")
		else:
			self.redirect("/latemeal")

class DeleteListing(webapp2.RequestHandler):

	def post(self):
		netid = self.request.get("netid")
		date = datetime.datetime.strptime(self.request.get("date"),
			"%Y-%m-%d %H:%M:%S.%f")
		oldListing = listing.Listing.query(listing.Listing.netid == netid,
			listing.Listing.date == date)
		for l in oldListing:
			print type(l)
			l.canceled=True
			l.put()
		self.redirect("/")
