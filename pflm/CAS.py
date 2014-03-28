import sys, os, cgi, md5, urllib, time, re, wsgiref, urlparse
form = cgi.FieldStorage()

admins = [u'usikder',u'madhavan',u'jtakahas']
SECRET = "5g34gan3z3hvj3ixnvij3nvlsioc82009bs3sjl3jvo49hw3vnutsniharjun"

class CASClient:
   def __init__(self):
      self.cas_url = 'https://fed.princeton.edu/cas/'
   def Authenticate(self, handler):
      query_params = {'service': self.ServiceURL()}
      # No valid ticket; redirect the browser to the login page to get one
      login_url = self.cas_url + 'login?' + urllib.urlencode(query_params)
      return handler.redirect(login_url, code = 307)
      #print 'Location: ' + login_url
      #print
      #print 'Status-line: HTTP/1.1 307 Temporary Redirect'
      #print ""
      sys.exit(0)

   def Validate(self, ticket):
      val_url = self.cas_url + "validate" + \
         '?service=' + urllib.quote(self.ServiceURL()) + \
         '&ticket=' + urllib.quote(ticket)
      r = urllib.urlopen(val_url).readlines()   # returns 2 lines
      if len(r) == 2 and re.match("yes", r[0]) != None:
        return r[1].strip().encode('ascii','replace')
      return None

   def ServiceURL(self):
      if os.environ.has_key('REQUEST_URI') is not None:
         # ret = 'http://' + os.environ['HTTP_HOST'] + os.environ['REQUEST_URI']
         ret = wsgiref.util.request_uri(os.environ)
         ret = re.sub(r'ticket=[^&]*&?', '', ret)
         ret = re.sub(r'\?&?$|&$', '', ret)
         return ret
         #$url = preg_replace('/ticket=[^&]*&?/', '', $url);
         #return preg_replace('/?&?$|&$/', '', $url);
      return "something is badly wrong"

#  Split string in exactly two pieces, return '' for missing pieces.
def split2(str,sep):
  parts = str.split(sep,1) + ["",""]
  return parts[0], parts[1]

#  Use hash and secret to encrypt string.
def makehash(str,secret=SECRET):
  m = md5.new()
  m.update(str)
  m.update(SECRET)
  return m.hexdigest()[0:8]
  
def CAS(handler):
    cookieKey = 'pforlmNETID'
    print handler.request.url
    C = CASClient()
    netid=""
    if cookieKey in handler.request.cookies:
      cookieVal=handler.request.cookies[cookieKey]
      oldhash=cookieVal[0:8]
      timestr, netid = split2(cookieVal[8:],":")
      newhash = makehash(timestr+":"+netid)
      if oldhash!=newhash:
        C.authenticate()
    else:
        if handler.request.get('ticket') != "":
            netid = C.Validate(
                handler.request.get('ticket'))
            url=handler.request.url
            u=urlparse.urlparse(url)
            qs = cgi.parse_qs(u.query)
            del(qs['ticket'])
            u = u._replace(query=urllib.urlencode(qs, True))
            url = urlparse.urlunparse(u)
            if netid != None:
              timestr = str(int(time.time()))
              cookieHash = makehash(timestr+ ":" + netid)
              cookieVal = cookieHash + timestr + ":" + netid
              handler.response.set_cookie(cookieKey,cookieVal,max_age=10)
              return handler.redirect(url)
            else:
              C.Authenticate(handler)
        else:
          print "authentication time"
          C.Authenticate(handler)
    if netid in admins:
      return netid
    else:
      return None

    
def main():
  print "CASClient does not run standalone"
if __name__ == '__main__':
  main()

