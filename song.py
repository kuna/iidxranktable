# make html
# and render to image
import urllib
import json

def getiidxinfo(user, type, lv):
	url = ('http://json.iidx.me/%s/%s/level/%d/' % (user, type, lv))
	res = urllib.urlopen(url)
	data = json.loads(res.read())
	return data

# dict: category -> songs[] (song)
def getCSVdata(csvpath):
	def processCode(code):
		# H/A/N confine command, ALL command
		attr = {}
		if (code == "ALL"):
			attr = {'option': 'ALL'}
		elif (not code[-1:].isdigit()):
			attr = {'id': code[:-1], 'option':code[-1:]}
		else:
			attr = {'id': code}
		return attr

	f = open(csvpath, 'rb')
	lines = f.readlines()
	f.close() 
	csvdata = []
	for l in lines:
		l = l.decode('utf8')
		l = l.replace('\n', '').replace('\r', '')
		arr = l.split('\t')
		arr = filter(None, arr)	# remove empty array
		songs = map(processCode, arr[1:])
		csvdata.append({'category': arr[0], 'songs': songs})
	return csvdata

# dict: category -> songs[] (title, code, clear, ex, ...)
def processCSV(musicdata, csvdata):
	def getdict(val):
		for music in musicdata:
			if (music['data']['id'] == val['id']):
				if (('option' in val and val['option'] == music['data']['diff']) or \
					'option' not in val):
					musicdata.remove(music);
					return music
		return None		

	# preprocess musicdata
	for music in musicdata:
		# ex: dpa -> A
		music['data']['diff'] = music['data']['diff'][-1:].upper()
		# change PLAY
		clear = int(music['clear'])
		if (clear == 0):
			music['clearstring'] = u'NO_PLAY'
		elif (clear == 1):
			music['clearstring'] = u'FAILED'
		elif (clear == 2):
			music['clearstring'] = u'ASSIST_CLEAR'
		elif (clear == 3):
			music['clearstring'] = u'EASY_CLEAR'
		elif (clear == 4):
			music['clearstring'] = u'CLEAR'
		elif (clear == 5):
			music['clearstring'] = u'HARD_CLEAR'
		elif (clear == 6):
			music['clearstring'] = u'EX-HARD_CLEAR'
		elif (clear == 7):
			music['clearstring'] = u'FULL_COMBO'

		# make rate
		if (music['score'] == None):
			music['rate'] = 0
		else:
			music['rate'] = music['score'] / float(music['data']['notes']) / 2 * 100
		
		# make rank
		if (music['rate'] >= 8.0/9*100):
			music['rank'] = u"AAA"
		elif (music['rate'] >= 7.0/9*100):
			music['rank'] = u"AA"
		elif (music['rate'] >= 6.0/9*100):
			music['rank'] = u"A"
		elif (music['rate'] >= 5.0/9*100):
			music['rank'] = u"B"
		elif (music['rate'] >= 4.0/9*100):
			music['rank'] = u"C"
		elif (music['rate'] >= 3.0/9*100):
			music['rank'] = u"D"
		elif (music['rate'] >= 2.0/9*100):
			music['rank'] = u"E"
		else:
			music['rank'] = u"F"

	# process r
	# this contains dictonaries, {category, songs=[]}
	r = []
	for category in csvdata:
		catearray = {}
		catearray['category'] = category['category']
		catearray['songs'] = []
		# if songid is ALL, then add all left songs.
		for song in category['songs']:
			if ('option' in song and song['option'] == 'ALL'):
				catearray['songs'] = musicdata
			else:
				record = getdict(song)
				if (record):
					# write difficulty if same song exists
					# ex: gigadelic [A]
					if ('option' in song):
						record['data']['title'] += " [" + record['data']['diff'] + "]"
					# add current song in current category
 					catearray['songs'].append(record)
				else:
					# this is for debugging.
					# if this message shows, then it's time to update data(txt) file.
					print "unknown song: %s" % (song['id'])

		# check out category lamp (clear)
		catearray['categoryclear'] = 7
		catearray['categoryclearstring'] = u'FULL_COMBO'
		for song in catearray['songs']:
			if (song['clear'] < catearray['categoryclear']):
				catearray['categoryclear'] = song['clear']
				catearray['categoryclearstring'] = song['clearstring']

		r.append(catearray)
	return r