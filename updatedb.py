import db
import parser_clddal, parser_clickagain, parser_zasa, parser_iidxme


def main():
	print 'opening DB ...'
	db_session = db.init_db()

	print 'parsing clickagain'
	clddal_db = parser_clddal.parse()

	print 'add to DB ...'
	added_data = 0
	for data in clddal_db:
		if not db.RankTable.query.filter(songname=data[0], songtype=data[1]).count():
			rankTable = db.RankTable(songname=data[0], songtype=data[1])
			db_session.add(rankTable)
			added_data = added_data+1
	db_session.commit()
	print "added %d datas" % added_data

	print 'finished. closing DB ...'
	db_session.remove()

if __name__ == '__main__':
	main()