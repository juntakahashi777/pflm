from bs4 import BeautifulSoup
import urllib, re, sys

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

print getName(sys.argv[1])