#-*- coding: utf-8 -*-
import iidx


def compile_data(ranktable, player, song_query):
	# if player is none, then all the information will be set null
	if (player == None):
		player = {}
		player['musicdata'] = None
		player['userdata'] = {}
		player['userdata']['djname'] = 'NONAME'
		player['userdata']['spclass'] = 0
		player['userdata']['dpclass'] = 0

	# create score data
	# [(category, [(songname, score, clear ...)])]
	score = addMetadata(player['musicdata'], ranktable, song_query)

	# make default user information
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

	# make information for return
	pageinfo = {
		'title': ranktable.tabletitle,
		'titlehtml': ranktable.tabletitle\
			.replace('SP', '<span style="color:red;">SP</span>')\
			.replace('DP', '<span style="color:#0099FF;">DP</span>')\
			.replace('Hard', '<span style="color:red;">Hard</span>')\

			.replace('Normal', '<span style="color:#0099FF;">Normal</span>'),
		'tablename': ranktable.tablename,
		'type': ranktable.type,
		'clearinfo': clearcount,
		'copyright': ranktable.copyright,
		'date': ranktable.time,
	}
	userinfo = {'name': name, 'spdan': iidx.getdanstring(spdan),
		'spdannum':spdan, 'dpdan': iidx.getdanstring(dpdan), 'dpdannum': dpdan}
	return userinfo, score, pageinfo

#	return render('rankview.html', {
#		option=option_,
#		user=,
#		clearcount=clearcount,
#		datas=score})

#
# addMetadata: push score data to user's musicdata
#
# dict: category -> songs[] (title, code, clear, ex, ...)
def addMetadata(musicdata, data, song_query):
	#
	# preprocess musicdata
	# - add 'rate', 'rank' to each song
	#
	if (musicdata == None):
		musicdata = []
		for song in song_query.filter(songtype__istartswith=data.type, songlevel=data.level).all():
			music = {
				'pkid': song.pk,
				'rate': 0,
				'rank': iidx.getrank(0),
				'clear': 0,
				'clearstring': iidx.getclearstring(0),
				'data': {
					'diff_detail': song.songtype,
					'diff': song.songtype[-1:],
					'title': song.songtitle,
					'id': song.songid,
				},
			}
			musicdata.append(music)
	else:
		for music in musicdata:
			# make diff(DP + A) string upper
			music['data']['diff_detail'] = music['data']['diff']
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

			# add song pk id
			song_obj = song_query.filter(songid=music['data']['id'], songtype=music['data']['diff_detail']).first()
			if (song_obj):
				music['pkid'] = song_obj.id
			else:
				music['pkid'] = -1

	# 
	# make processed array
	# - find each song data's category and add to that array
	#
	categories = []				# processed category datas
	categories_prefetch = []	# prefetched category datas from DB
	for category in data.rankcategory_set.all():
		items = []
		for item in category.rankitem_set.all():
			items.append(item)
		categories_prefetch.append({'categoryname': category.categoryname, 'items': items})
	def getCategory(categoryname):
		for category in categories:
			if (category['category'] == categoryname):
				return category
		# if category is not exist, then make new one
		category = { 'category': categoryname, 
				'songs': [],
				'categoryclearstring': u'FULL_COMBO',
				'categoryclear': 7 }	# default setting
		categories.append(category)
		return category
	def getCategoryName(songpkid):
		for category in categories_prefetch:
			for item in category['items']:
				# ASSERT! some deleted song may have no 'song relation item'
				# ASSERT! item's difficulty(type) must considered)
				if (item.song \
					and item.song.id == int(songpkid)):
					return category['categoryname']
		return None		# cannot find category

	for music in musicdata:
		category = getCategoryName(music['pkid'])
		if (category == None):
			getCategory("-")['songs'].append(music)
		else:
			getCategory(category)['songs'].append(music)

	#
	# category lamp process
	#
	for catearray in categories:
		for song in catearray['songs']:
			if (song['clear'] < catearray['categoryclear']):
				catearray['categoryclear'] = song['clear']
				catearray['categoryclearstring'] = song['clearstring']

	# process category sorting
	def sort_func(x, y):
		def getValue(_x):
			x = _x['category']
			order_arr = (
				u'Leggendaria',
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
				u'1기',
				u'10+')
			if (x == '-'):
				return 999
			elif (x in order_arr):
				return order_arr.index(x)
			else:
				try:
					return 100-int(float(x.replace("N", ""))*10)
				except:
					return 100
		# make score
		# bigger: later
		return getValue(x) - getValue(y)
	return sorted(categories, cmp=sort_func)

