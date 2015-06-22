#-*- coding: utf-8 -*-

from flask import Flask, render_template, abort
import iidx
import jsondata
import song
import db

def render_score(player, score, option_):
	name = ""
	spdan = ""
	dpdan = ""
	if (player):
		name = player['userdata']['djname']
		spdan = player['userdata']['spclass']
		dpdan = player['userdata']['dpclass']

	# count clear counts
	clearcount = {
		'noplay': 0,
		'failed': 0,
		'assist': 0,
		'easy': 0,
		'normal': 0,
		'hard': 0,
		'exhard': 0,
		'fullcombo': 0
	}
	for category in score:
		for x in category['songs']:
			clearcount['noplay'] = clearcount['noplay'] + (x['clear'] == 0)
			clearcount['failed'] = clearcount['failed'] + (x['clear'] == 1)
			clearcount['assist'] = clearcount['assist'] + (x['clear'] == 2)
			clearcount['easy'] = clearcount['easy'] + (x['clear'] == 3)
			clearcount['normal'] = clearcount['normal'] + (x['clear'] == 4)
			clearcount['hard'] = clearcount['hard'] + (x['clear'] == 5)
			clearcount['exhard'] = clearcount['exhard'] + (x['clear'] == 6)
			clearcount['fullcombo'] = clearcount['fullcombo'] + (x['clear'] == 7)

	return render_template('rankview.html', option=option_,
		user={'name': name, 'spdan': iidx.getdanstring(spdan),
			'spdannum':spdan, 'dpdan': iidx.getdanstring(dpdan), 'dpdannum': dpdan},
		clearcount=clearcount,
		datas=score)

def render_songlist(data, userjson):
	# parse web (get player json file)
	# TODO if no user required, just render it without clear graph
	player = jsondata.loadJSONurl(userjson)
	if (player == None or 'userdata' not in player or player['status'] != 'success'):
		print "userdata not found"
		abort(404)	# should show abort(404)
		return

	# create score data
	# [(category, [(songname, score, clear ...)])]
	score = addMetadata(player['musicdata'], data)

	# make title HTML
	titlehtml = data.tabletitle\
		.replace('SP', '<span style="color:red;">SP</span>')\
		.replace('DP', '<span style="color:#0099FF;">DP</span>')\
		.replace('Hard', '<span style="color:red;">Hard</span>')\
		.replace('Groove', '<span style="color:#0099FF;">Groove</span>')

	option = {
		'title': data.tabletitle,
		'type': data.type,
		'titlehtml': titlehtml,
		'from': data.copyright,
		'date': data.time.strftime("%d %b %Y")
	}

	return render_score(player, score, option)

#
# addMetadata: push score data to user's musicdata
#
# dict: category -> songs[] (title, code, clear, ex, ...)
def addMetadata(musicdata, data):
	#
	# preprocess musicdata
	# - add 'rate', 'rank' to each song
	#
	for music in musicdata:
		# make diff(DPA) string upper
		music['data']['diff'] = music['data']['diff'][-1:].upper()

		# add clear metadata (number to readable string)
		clear = int(music['clear'])
		music['clearstring'] = iidx.getclearstring(clear)

		# make rate (sometimes note data isn't provided -> 0)
		if (music['score'] == None or music['data']['notes'] == None):
			music['rate'] = 0
		else:
			music['rate'] = music['score'] / float(music['data']['notes']) / 2 * 100
		
		# make rank
		music['rank'] = iidx.getrank(music['rate'])

	# 
	# make processed array
	# - find each song data's category and add to that array
	#
	r = []
	def getCategory(categoryname):
		for r_ in r:
			if (r_['category'] == categoryname):
				return r_
		r_ = { 'category': categoryname, 
				'songs': [],
				'categoryclearstring': u'FULL_COMBO',
				'categoryclear': 7 }	# default setting
		r.append(r_)
		return r_
	def getCategoryName(songid):
		for category in data.category:
			for item in category.rankitem:
				# ASSERT! some deleted song may have no 'song relation item'
				if (item.song and item.song.songid == int(songid)):
					return category.categoryname
		return None		# cannot find category

	for music in musicdata:
		category = getCategoryName(music['data']['id'])
		if (category == None):
			getCategory("-")['songs'].append(music)
		else:
			getCategory(category)['songs'].append(music)

	#
	# category lamp process
	#
	for catearray in r:
		for song in catearray['songs']:
			if (song['clear'] < catearray['categoryclear']):
				catearray['categoryclear'] = song['clear']
				catearray['categoryclearstring'] = song['clearstring']

	# process category sorting
	def sort_func(x, y):
		def getValue(_x):
			x = _x['category']
			order_arr = (
				u'Leggenderia',
				u'처리력 S+',
				u'개인차 S+',
				u'처리력 S',
				u'개인차 S',
				u'처리력 A+',
				u'개인차 A+',
				u'처리력 A',
				u'개인차 A',
				u'처리력 B+',
				u'개인차 B+',
				u'처리력 B',
				u'개인차 B',
				u'처리력 C',
				u'개인차 C',
				u'처리력 D',
				u'개인차 D',
				u'처리력 E',
				u'개인차 E',
				u'처리력 F',
				u'7기',
				u'6기',
				u'5기',
				u'4기',
				u'3기',
				u'2기',
				u'1기')
			if (x == '-'):
				return 999
			elif (x in order_arr):
				return order_arr.index(x)
			else:
				try:
					return 100-int(float(x)*10)
				except:
					return 100
		# make score
		# bigger: later
		return getValue(x) - getValue(y)
	return sorted(r, cmp=sort_func)


#
# ------------------ customs (view) -------------------------
#

def render_table(tablename, username):
	#load from DB
	data = db.RankTable.query.filter_by(tablename=tablename).one()
	userjson = "http://json.iidx.me/%s/%s/level/%d/" % (username, data.type.lower(), data.level)
	return render_songlist(data, userjson)