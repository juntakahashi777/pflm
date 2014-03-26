import sys, os, cgi, urllib, re, wsgiref, urlparse
form = cgi.FieldStorage()
class CASClient:
   def __init__(self):
      self.cas_url = 'https://fed.princeton.edu/cas/'
   def Authenticate(self, handler):
      # If the request contains a login ticket, try to validate it
      form = cgi.FieldStorage()
      if form.has_key('ticket'):
         netid = self.Validate(form['ticket'].value)
         if netid != None:
            return netid
      # No valid ticket; redirect the browser to the login page to get one
      login_url = self.cas_url + 'login' \
         + '?service=' + urllib.quote(self.ServiceURL())
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
         return r[1].strip()
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

def CAS(handler):
    cookieKey = 'pforlmNETID'
    C = CASClient()
    netid=""
    if cookieKey in handler.request.cookies:
        netid=handler.request.cookies[cookieKey]
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
                handler.response.set_cookie(cookieKey,netid,max_age=10)
                return handler.redirect(url)
            else:
                C.Authenticate(handler)
        else:
            C.Authenticate(handler)
    return netid
    
def main():
  print "CASClient does not run standalone"
if __name__ == '__main__':
  main()

