#!/usr/local/python/current/bin/python
import CASClient
C = CASClient.CASClient()
netid = C.Authenticate()
print "Content-Type: text/html"
print ""
import os
print "<b>hello from the other side</b>"
print os.environ
print "<p><b>done</b>"
