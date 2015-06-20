import db
import parser_clickagain, parser_zasa, parser_iidxme


def main():
	print 'opening DB ...'
	db_session = db.init_db()

	for lvl in range(12, 13):
		print 'parsing iidxme sp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "sp")
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

	print 'parsing clickagain'
	# TODO

	print 'finished. closing DB ...'
	db_session.remove()

if __name__ == '__main__':
	main()