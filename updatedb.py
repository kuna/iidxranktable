#-*- coding: utf-8 -*-

import db
import parser_clickagain, parser_zasa, parser_iidxme, parser_custom
import textdistance

def update_iidxme():
	def update(data):
		added_data = 0
		for song in data:
			if not db.Song.query.filter_by(songid=song['id'], songtype=song['diff']).count():
				song = db.Song(songtitle=song['title'], 
					songtype=song['diff'],
					songid=song['id'],
					songlevel=song['level'],
					songnotes=song['notes'])
				db_session.add(song)
				added_data = added_data+1
		db_session.commit()
		print "added %d datas" % added_data

	for lvl in range(6, 13):
		print 'parsing iidxme sp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "sp")
		update(data)

	for lvl in range(6, 13):
		print 'parsing iidxme dp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "dp")
		update(data)

def updateDB(data, tablename, tabletitle, copyright, type, level):
	added_data = 0

	# get table first
	table = db.RankTable.query.filter_by(tablename=tablename)
	if (not table.count()):
		table = db.RankTable(tablename=tablename,
			tabletitle=tabletitle,
			copyright = copyright,
			type=type,
			level=level)
		db_session.add(table)
	else:
		table = table.one()
		# update table info
		table.tabletitle = tabletitle
		table.type = type
		table.level = level
		table.copyright = copyright

	# process items
	for group in data:
		# before adding items, get category first
		category = db.RankCategory.query.filter_by(table_id=table.id, categoryname=group[0])
		if (not category.count()):
			category = db.RankCategory(table_id=table.id, categoryname=group[0])
			# append category to group
			table.category.append(category)
			db_session.add(category)
		else:
			category = category.one()

		# make rank item
		# if already exists then update category only
		for item in group[1]:
			rankitem = db.RankItem.query.filter_by(category_id=category.id, songtitle=item[0], songtype=item[1])
			if not rankitem.count():
				rankitem = db.RankItem(songtitle=item[0], 
					songtype=item[1],
					category_id=category.id)
				# append item to category
				category.rankitem.append(rankitem)
				db_session.add(rankitem)
				added_data = added_data+1
			else:
				rankitem[0].category_id = category.id

	db_session.commit()
	print "added %d datas" % added_data

def update_SP():
	print 'parsing 2ch'
	updateDB(parser_custom.parse12(), "SP12_2ch", 
		u"Beatmania IIDX SP lv.12 Hard Guage Rank",
		u"copyright",
		"SP", 12)
	print 'parsing clickagain'
	updateDB(parser_clickagain.parse12_7(), "SP12_7", 
		u"Beatmania IIDX SP lv.12 7記 Hard Guage Rank",
		u"copyright", 
		"SP", 12)
	updateDB(parser_clickagain.parse12(), "SP12", 
		u"Beatmania IIDX SP lv.12 Hard Guage Rank",
		u"copyright", 
		"SP", 12)
	updateDB(parser_clickagain.parse11(), "SP11", 
		u"Beatmania IIDX SP lv.11 Hard Guage Rank",
		u"copyright", 
		"SP", 11)
	updateDB(parser_clickagain.parse10(), "SP10", 
		u"Beatmania IIDX SP lv.10 Hard Guage Rank",
		u"copyright", 
		"SP", 10)

def update_DP():
	print 'parsing zasa'
	updateDB(parser_zasa.parse12(), "DP12", 
		u"Beatmania IIDX DP lv.12 Rank", 
		u"copyright", 
		"DP", 12)
	updateDB(parser_zasa.parse11(), "DP11", 
		u"Beatmania IIDX DP lv.11 Rank", 
		u"copyright", 
		"DP", 11)
	updateDB(parser_zasa.parse10(), "DP10", 
		u"Beatmania IIDX DP lv.10 Rank", 
		u"copyright", 
		"DP", 10)

#
# suggest similar song object from name/diff
#
def smart_suggestion(name, diff, level):
	import sys
	# first get all song data
	songs = db.Song.query.filter_by(songtype=diff)\
		.filter(db.Song.songlevel == level)

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
		print "cannot find matching one, but some suggestion was found"
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
			return db.Song.query.filter_by(songtype=diff, songtitle=suggestions[code-1][0]).one()
		elif (code < 0):
			# search song which that code exists
			songs = db.Song.query.filter_by(songtype=diff, songid=-code)
			# if not then loop again
			if not songs.count():
				print 'no song of such code exists'
				continue
			else:
				song = songs.one()
				print 'you selected song [%s]. if okay then [y]' % song.songtitle
				okay = raw_input("> ")
				if (okay == "y"):
					return song
				else:
					print 'canceled.'
					continue

#
# make relation with song
#
def update_relation():
	print 'making relation with song table ...'
	# scan rankitem one by one
	updated_cnt = 0
	for item in db.RankItem.query.all():
		if (item.song_id == None):
			# if song_id not set, scan it
			print 'current: %s' % item.songtitle
			songs = db.Song.query.filter_by(songtitle=item.songtitle, songtype=item.songtype)
			if songs.count() <= 0:
				# do smart suggestion
				song = smart_suggestion(item.songtitle, item.songtype, item.category.ranktable.level)
				if (song != None):
					item.song_id = song.id
				db_session.commit()
			else:
				song = songs.one()
				#song.rankitem.append(item)
				item.song_id = song.id
		updated_cnt += 1

	print "%d items updated." % updated_cnt
	db_session.commit()


def main():
	#
	# you should execute it through IDLE because of unicode
	#

	print 'opening DB ...'
	global db_session
	db_session = db.init_db()

	#update_iidxme()

	#update_SP()

	#update_DP()

	update_relation()

	print 'finished. closing DB ...'
	db_session.remove()

if __name__ == '__main__':
	main()