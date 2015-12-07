#-*- coding: utf-8 -*-
#
# algorithm from: http://walkure.net/hakkyou/komakai.html#komakaihanashi
#
import db
import math
import parser_iidxme
import time
from datetime import datetime

# crolling user's information
def update_songs():
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
		print "added %d datas" % added_data

	for lvl in range(8, 13):
		print 'parsing iidxme sp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "sp")
		update(data)

	for lvl in range(8, 13):
		print 'parsing iidxme dp (%d)' % lvl
		data = parser_iidxme.parse_songs(lvl, "dp")
		update(data)


def update_user():
	add_count = 0
	for user in parser_iidxme.parse_users():
		player_query = db.Player.query.filter_by(iidxid=user[2])
		if (player_query.count()):
			# edit nickname
			player = player_query.one()
			player.iidxnick = user[0]
			player.iidxmeid = user[1]
		else:
			# add new user
			player = db.Player(iidxid=user[2], 
					iidxnick=user[0],
					iidxmeid=user[1],
					sppoint=0,
					dppoint=0,
					spclass=0,
					dpclass=0,
					splevel=0,
					dplevel=0)
			db_session.add(player)
			add_count += 1
	db_session.commit()
	print 'added %d items' % add_count

def update_user_from_data(player, user_info):
	add_count = 0
	# add clear data
	for playrecord in user_info['musicdata']:
		if (playrecord['clear'] > 2):	# only over assist clear
			song = db.Song.query.filter_by(songid=playrecord['data']['id'], songtype=playrecord['data']['diff'].upper())
			if (not song.count()):
				continue
			else:
				song = song.one()
			playrecord_query = db.PlayRecord.query.filter_by(player_id=player.id, song_id=song.id)
			if (playrecord_query.count()):
				# just update clear
				pr = playrecord_query.one()
				if (playrecord['score']):
					pr.playscore = playrecord['score']
				if (playrecord['miss']):
					pr.playmiss = playrecord['miss']
				pr.playclear = playrecord['clear']
			else:
				# add new one
				pr = db.PlayRecord(playscore=playrecord['score'],
					playclear=playrecord['clear'],
					playmiss=playrecord['miss'],
					player_id=player.id,
					song_id=song.id)
				db_session.add(pr)
				add_count += 1

	return add_count

def update_single_user_by_name(iidxmeid):
	return update_single_user(db.Player.query.filter_by(iidxmeid=iidxmeid).one())

def update_single_user(player):
	add_count = 0
	sppoint = 0
	dppoint = 0
	spclass = 0
	dpclass = 0
	# start from level 8
	for mode in ("sp", "dp"):
		for i in range(8, 13):
			try:
				print 'updating user %s (%s) - (%s, %d) ...' % (player.iidxmeid, player.iidxnick, mode, i)
				user_info = parser_iidxme.parse_user(player.iidxmeid, mode, i)
				sppoint = user_info['userdata']['sppoint']
				dppoint = user_info['userdata']['dppoint']
				spclass = user_info['userdata']['spclass']
				dpclass = user_info['userdata']['dpclass']
				add_count += update_user_from_data(player, user_info)
				time.sleep(0.5)		# to avoid suspend as traffic abusing
			except (KeyboardInterrupt, SystemExit):
				print 'bye'
				exit()
			except:
				print 'error during parsing. ignore error and continue'
	player.sppoint = sppoint
	player.dppoint = dppoint
	player.spclass = spclass
	player.dpclass = dpclass
	player.time = datetime.utcnow()

	return add_count

def update_user_information():
	add_count = 0
	for player in db.Player.query.all():
		add_count += update_single_user(player)
		print 'added %d playrecord' % add_count
		db_session.commit()

def main():
	print 'opening DB ...'
	global db_session
	db_session = db.init_db()

	"""
	print 'remove all player & playdata'
	db.Player.query.delete()
	db.PlayRecord.query.delete()

	print 'updating songs'
	update_songs()

	print 'crolling user list ...'
	update_user()
	"""
	print 'crolling user information ...'
	update_user_information()

	print 'finished. closing DB ...'
	db_session.commit()
	db_session.remove()


if __name__=="__main__":
	main()