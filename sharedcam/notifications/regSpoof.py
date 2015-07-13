
import urllib2
import json

REG_URL = "http://sharedcam.paldeploy.com/registry/regp/"
url = REG_URL+"?name=bob&room=1234567890&state=1&clientType=spoof"
val = urllib2.urlopen(url).read()
print "val", val

