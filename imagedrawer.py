# make html
# and render to image
import urllib
import json

def getSPinfo(user, lv):
	url = ('http://json.iidx.me/%s/sp/level/%d/' % (user, lv))
	res = urllib.urlopen(url)
	data = json.loads(res.read())
	return data

print getSPinfo('kuna', 12)