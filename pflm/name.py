from bs4 import BeautifulSoup
import urllib, re, sys

def getName(netid):
	url = 'http://www.princeton.edu/main/tools/search/index.xml?q='+netid
	f = urllib.urlopen(url)
	html = f.read()
	soup = BeautifulSoup(html)
	soup = soup.find("div", {"id": "search-people-results"})
	for person in soup.find_all("li"):
		if person.find("a", {"href": re.compile(netid+"@princeton.edu")}) is not None:
			name = person.find("a", {"class": "collapsed"}).get_text()
			return name.split(',')[1].split()[0]

print getName(sys.argv[1])