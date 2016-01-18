#-*- coding: utf-8 -*-
#
# algorithm from: http://walkure.net/hakkyou/komakai.html#komakaihanashi
#
import db
import math
import parser_iidxme
import time
from datetime import datetime, date
import log

db_session = db.get_session()

# crolling user's information
def update_songs():
	log.Print('updating songs')
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
		log.Print("added %d datas" % added_data)

	for lvl in range(8, 13):
		log.Print('parsing iidxme sp (%d)' % lvl)
		data = parser_iidxme.parse_songs(lvl, "sp")
		update(data)

	for lvl in range(8, 13):
		log.Print('parsing iidxme dp (%d)' % lvl)
		data = parser_iidxme.parse_songs(lvl, "dp")
		update(data)

def add_user(user):
	player_query = db_session.query(db.Player).filter_by(iidxid=user[2])
	if (player_query.count()):
		# edit nickname
		player = player_query.one()
		player.iidxnick = user[0]
		player.iidxmeid = user[1]
		return 0
	else:
		# add new user
		player = db.Player(iidxid=user[2], 
				iidxnick=user[0],
				iidxmeid=user[1],
				time=datetime.min,
				sppoint=0,
				dppoint=0,
				spclass=0,
				dpclass=0,
				splevel=0,
				dplevel=0)
		db_session.add(player)
		return 1

def update_user():
	add_count = 0
	for user in parser_iidxme.parse_users():
		add_count += add_user(user)
	db_session.commit()
	log.Print('added %d items' % add_count)

def update_user_from_data(player, user_info):
	add_count = 0
	# add clear data
	for playrecord in user_info['musicdata']:
		if (playrecord['clear'] >= 1):	# over failed user
			song = db.Song.query.filter_by(songid=playrecord['data']['id'], songtype=playrecord['data']['diff'].upper())
			if (not song.count()):
				continue
			else:
				song = song.one()
			playrecord_query = db_session.query(db.PlayRecord).filter_by(player_id=player.id, song_id=song.id)
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
	return update_single_user(db_session.query(db.Player).filter_by(iidxmeid=iidxmeid).one())

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
				log.Print('updating user %s (%s) - (%s, %d) ...' % (player.iidxmeid, player.iidxnick, mode, i))
				user_info = parser_iidxme.parse_user(player.iidxmeid, mode, i)
				sppoint = user_info['userdata']['sppoint']
				dppoint = user_info['userdata']['dppoint']
				spclass = user_info['userdata']['spclass']
				dpclass = user_info['userdata']['dpclass']
				add_count += update_user_from_data(player, user_info)
				time.sleep(0.1)		# to avoid being suspend as traffic abusing
			except (KeyboardInterrupt, SystemExit):
				log.Print('bye')
				exit()
			except:
				log.Print('error during parsing. ignore error and continue')
	player.sppoint = sppoint
	player.dppoint = dppoint
	player.spclass = spclass
	player.dpclass = dpclass
	player.time = datetime.utcnow()

	return add_count

def update_user_information():
	log.Print('crolling user information ...')
	add_count = 0
	for player in db.Player.query.all():
		add_count += update_single_user(player)
		log.Print('added %d playrecord' % add_count)
		db_session.commit()

def main():
	update_user()

	update_user_information()

	log.Print('finished. closing DB ...')
	db.commit()
	db.remove()


if __name__=="__main__":
	main()
