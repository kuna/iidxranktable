#-*- coding: utf-8 -*-
import json
import copy
import urllib

jsonData = {}
textData = {}

def loadJSONurl(url):
	try:
		res = urllib.urlopen(url)
		data = json.loads(res.read())
		return data
	except Exception, e:
		print('Error in json.loadJSONurl: ' + str(e))
		return None

def getiidxinfo(user, type, lv):
	url = ('http://json.iidx.me/%s/%s/level/%d/' % (user, type, lv))
	return loadJSONurl(url)

# error: None, returns json array.
def readjson(path):
	f = open(path, 'rb');
	if (f == None):
		return None
	data = json.load(f)
	f.close()
	return data

# just read only once.
def loadJSONfile(path):
	if (path not in jsonData):
		jsonData[path] = readjson(path)
	# duplicate
	return copy.deepcopy(jsonData[path])

# just read only once.
def loadTextfile(path):
	if (path not in textData):
		f = open(path, 'rb')
		if (f == None):
			textData[path] = None
		else:
			textData[path] = f.read()
			f.close()
	# duplicate
	return copy.copy(textData[path])
