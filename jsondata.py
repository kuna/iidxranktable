#-*- coding: utf-8 -*-
import json

jsonData = {}
textData = {}

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
	return jsonData[path]

# just read only once.
def loadTextfile(path):
	if (path not in textData):
		f = open(path, 'rb')
		if (f == None):
			textData[path] = None
		else:
			textData[path] = f.read()
			f.close()
	return textData[path]