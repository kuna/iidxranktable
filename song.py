# make html
# and render to image
import urllib
import json

def getSPinfo(user, lv):
	url = ('http://json.iidx.me/%s/sp/level/%d/' % (user, lv))
	res = urllib.urlopen(url)
	data = json.loads(res.read())
	return data

# dict: category -> songs[] (song)
def getCSVdata(csvpath):
	f = open(csvfile, 'rb')
	lines = f.readlines()
	f.close()
	csvdata = []
	for l in lines:
		arr = l.split('\t')
		songs = map(lambda x: {'id': x}, arr[1:])
		csvdata.append({'category': arr[0], 'songs': arr[1:]})
	return csvdata

# dict: category -> songs[] (title, code, clear, ex, ...)
def processCSV(musicdata, csvdata):
	for category in csvdata:
		for song in category.songs:
			record = musicdata.get('id', song.id)
			if (record):
				category.songs.get('id', song.id) = record
	return csvdata

#print getSPinfo('kuna', 12)