# make html
# and render to image
import urllib
import json
import iidx
import jsondata

# dict: category -> songs[] (song)
def getCSVdata(csvpath):
	def processCode(code):
		# H/A/N confine command, ALL command
		attr = {}
		if (code == "ALL"):
			attr = {'id': None, 'option': 'ALL'}
		elif (not code[-1:].isdigit()):
			attr = {'id': code[:-1], 'option':code[-1:]}
		else:
			attr = {'id': code, 'option': None}
		return attr

	lines = jsondata.loadTextfile(csvpath).split('\n')
	csvdata = []
	for l in lines:
		if (l == ""):
			continue
		l = l.decode('utf8')
		l = l.replace('\n', '').replace('\r', '')
		arr = l.split('\t')
		arr = filter(None, arr)	# remove empty array
		songs = map(processCode, arr[1:])
		csvdata.append({'category': arr[0], 'songs': songs})
	return csvdata

# check is data exists(rank table data) in musicdata(user data).
# if rank item exists in user's record, return record
# if all of the recorddata OKAY, return True
# else, return None (False)
def isexists(recorddata, rankitem, removeprevious=False):
	if (rankitem['option'] == 'ALL'):
		return True
	else:
		for music in recorddata:
			if (music['data']['id'] == rankitem['id']):
				if (rankitem['option'] == None or rankitem['option'].upper() == music['data']['diff'][-1:].upper()):
					if removeprevious:
						recorddata.remove(music)
					return music
	return None

# dict: category -> songs[] (title, code, clear, ex, ...)
def processCSV(musicdata, csvdata):
	# preprocess musicdata
	for music in musicdata:
		# ex: dpa -> A
		music['data']['diff'] = music['data']['diff'][-1:].upper()
		# change PLAY
		clear = int(music['clear'])
		music['clearstring'] = iidx.getclearstring(clear)

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
			record = isexists(musicdata, song)
			if (record == True):
				catearray['songs'] = musicdata
			else:
				if (record):
					# write difficulty if same song exists
					# ex: gigadelic [A]
					if (song['option'] != None):
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