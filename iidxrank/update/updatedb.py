#-*- coding: utf-8 -*-

import parser_clickagain, parser_zasa, parser_iidxme, parser_custom
import textdistance
import datetime

def update_iidxme():
	global models
	def update(data):
		songs = models.Song.objects.all()
		added_data = 0
		for song in data:
			song_query = models.Song.objects.filter(songid=song['id'], songtype=song['diff'])
			if not song_query.count():
				if song['notes'] == None:
					song['notes'] = 0
				models.Song.objects.create(
					songtitle=song['title'], 
					songtype=song['diff'],
					songid=song['id'],
					songlevel=song['level'],
					songnotes=song['notes'],
					version=song['version'],
				)
				added_data = added_data+1
			else:
				# just make update you want
				song_obj = song_query.first()
				song_obj.version = song['version']
				song_obj.save()
		print "added %d datas" % added_data

	for lvl in range(6, 13):
		print 'parsing iidxme sp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "sp")
		update(data)

	for lvl in range(6, 13):
		print 'parsing iidxme dp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "dp")
		update(data)

# update or create rank table
def updateDB(data, tablename, tabletitle, level):
	global models
	added_data = 0

	# get table first
	table = models.RankTable.objects.filter(tablename=tablename)
	if (not table.count()):
		table = RankTable.objects.create(tablename=tablename,
			tabletitle=tabletitle,
			copyright = '',
			type='',
			level=0)
		table.save()
	else:
		table = table.first()
		# update table info
		table.tabletitle = tabletitle
		table.save()

	# process rankitems/rankcategories
	for group in data:
		# before adding items, get category first
		category = models.RankCategory.objects.filter(ranktable=table, categoryname=group[0])
		if (not category.count()):
			category = models.RankCategory(ranktable=table, categoryname=group[0])
			category.save()
		else:
			category = category.first()

		# make rank item
		# if already exists then update category only
		for item in group[1]:
			song_tag = item[0] + "," + item[1]
			rankitem = models.RankItem.objects.filter(rankcategory=category, info=song_tag)
			if not rankitem.count():
				# search song automatically from DB
				song = models.Song.objects.filter(songtitle=item[0], songtype=item[1], songlevel=level)
				if (not song.count()):
					song = smart_suggestion(item[0], item[1], level)	# name, diff, level
					if (song == None):
						continue	# ignore
				else:
					song = song.first()
				rankitem = models.RankItem(info=song_tag,
					rankcategory=category,
					song= song)
				# append item to category
				rankitem.save()
			else:
				rankitem = rankitem.first()
				rankitem.category = category
				rankitem.save()

	print "added %d datas" % added_data

def update_SP():
	print 'parsing 2ch'
	updateDB(parser_custom.parse12(), "SP12_2ch", 
		u"Beatmania IIDX SP lv.12 Hard Guage Rank", 12)
	print 'parsing clickagain'
	updateDB(parser_clickagain.parse12_7(), "SP12_7", 
		u"Beatmania IIDX SP lv.12 7記 Hard Guage Rank", 12)
	updateDB(parser_clickagain.parse12(), "SP12", 
		u"Beatmania IIDX SP lv.12 Hard Guage Rank", 12)
	updateDB(parser_clickagain.parse11(), "SP11", 
		u"Beatmania IIDX SP lv.11 Hard Guage Rank", 11)
	updateDB(parser_clickagain.parse10(), "SP10", 
		u"Beatmania IIDX SP lv.10 Hard Guage Rank", 10)
	updateDB(parser_clickagain.parse9(), "SP9", 
		u"Beatmania IIDX SP lv.9 Hard Guage Rank", 9)
	updateDB(parser_clickagain.parse8(), "SP8", 
		u"Beatmania IIDX SP lv.8 Hard Guage Rank", 8)
	# groove
	updateDB(parser_clickagain.parse12N(), "SP12N", 
		u"Beatmania IIDX SP lv.12 Normal Guage Rank", 12)
	updateDB(parser_clickagain.parse11N(), "SP11N", 
		u"Beatmania IIDX SP lv.11 Normal Guage Rank", 11)
	updateDB(parser_clickagain.parse10N(), "SP10N", 
		u"Beatmania IIDX SP lv.10 Normal Guage Rank", 10)
	updateDB(parser_clickagain.parse9N(), "SP9N", 
		u"Beatmania IIDX SP lv.9 Normal Guage Rank", 9)
	updateDB(parser_clickagain.parse8N(), "SP8N", 
		u"Beatmania IIDX SP lv.8 Normal Guage Rank", 8)

def update_DP():
	print 'parsing zasa'
	updateDB(parser_zasa.parse12(), "DP12", 
		u"Beatmania IIDX DP lv.12 Rank", 12)
	updateDB(parser_zasa.parse11(), "DP11", 
		u"Beatmania IIDX DP lv.11 Rank", 11) 
	updateDB(parser_zasa.parse10(), "DP10", 
		u"Beatmania IIDX DP lv.10 Rank", 10) 
	updateDB(parser_zasa.parse9(), "DP9", 
		u"Beatmania IIDX DP lv.9 Rank", 9) 
	updateDB(parser_zasa.parse8(), "DP8", 
		u"Beatmania IIDX DP lv.8 Rank", 8) 
	updateDB(parser_zasa.parse7(), "DP7", 
		u"Beatmania IIDX DP lv.7 Rank", 7) 
	updateDB(parser_zasa.parse6(), "DP6", 
		u"Beatmania IIDX DP lv.6 Rank", 6)

#
# suggest similar song object from name/diff
#
def smart_suggestion(name, diff, level):
	import sys
	global models
	# first get all song data
	songs = models.Song.objects.filter(songtype=diff, songlevel=level).all()

	# make new array for suggestion
	title_arr = []
	for item in songs:
		title_arr.append(item.songtitle)

	# and call 'textdistance'
	suggestions = textdistance.getNearTextDistance(title_arr, name)[:5]

	# remake song array
	#sug_songs = []
	#for sug_title in suggestions:
	#	sug_songs.append()

	while (1):
		print("cannot find matching one(%s / %s / %d), but some suggestion was found" % (name, diff, level))
		idx = 1
		print "0. (deleted)"
		for sug_title in suggestions:
			print "%d. %s (%s)" % (idx, sug_title[0], diff)
			idx += 1
		print "enter the song you want or enter song code you want in negative"
		print "(ex: -23456)"
		code = 0
		try:
			code = int(raw_input("> "))
		except ValueError:
			print "enter correct value"
			continue

		if (code == 0):
			return None
		elif (code > 0):
			if (code > len(suggestions)):
				print 'out of suggestions'
				continue
			return models.Song.objects.filter(songtype=diff, songtitle=suggestions[code-1][0]).first()
		elif (code < 0):
			# search song which that code exists
			songs = models.Song.objects.filter(songtype=diff, songid=-code)
			# if not then loop again
			if not songs.count():
				print 'no song of such code exists'
				continue
			else:
				song = songs.first()
				print 'you selected song [%s]. if okay then [y]' % song.songtitle
				okay = raw_input("> ")
				if (okay == "y"):
					return song
				else:
					print 'canceled.'
					continue

#
# make relation with song
# it's currently depreciated ...
#
def update_relation():
	print 'making relation with song table ...'
	# scan rankitem one by one
	updated_cnt = 0
	for item in models.RankItem.query.all():
		if (item.song_id == None):
			# if song_id not set, scan it
			print 'current: %s' % item.songtitle
			songs = models.Song.objects.filter(songtitle=item.songtitle, songtype=item.songtype)
			if songs.count() <= 0:
				# do smart suggestion
				song = smart_suggestion(item.songtitle, item.songtype, item.category.ranktable.level)
				if song == None:
					continue
				item.song_id = song.id
				song.save()
			else:
				song = songs.first()
				#song.rankitem.append(item)
				item.song_id = song.id
		updated_cnt += 1

	print "%d items updated." % updated_cnt


# message part
outputmsgs = []
inputmsgs = []

def output(message):
	global outputmsgs
	outputmsgs.append(message)

def getRecentMsgs():
	global outputmsgs
	return outputmsgs

def sendMessage(message):
	global inputmsgs
	inputmsgs.append(message)

def pollMessage():
	import time
	global inputmsgs
	while (len(inputmsgs <= 0)):
		time.sleep(0.1)
	return inputmsgs.pop(0)



def setModel(_models):
	global models
	models = _models


def main():
	#
	# you should execute it through IDLE because of unicode
	#

	update_iidxme()

	#update_SP()

	update_DP()

	#update_relation()

if __name__ == '__main__':
	main()
