from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Song(db.Model):
	id = db.Column('object_id', db.Integer, primary_key=True, index=True)
	records = db.relationship('PlayRecord', backref='song', lazy='select')

	songid = db.Column('songid', db.Integer)
	songtype = db.Column('songtype', db.String(8))		# dph/spa ...
	songtitle = db.Column('songtitle', db.String(40))
	songlevel = db.Column('songlevel', db.Integer)
	songnotes = db.Column('songnotes', db.Integer)

class PlayRecord(db.Model):
	__tablename__ = 'play'
	id = db.Column('object_id', db.Integer, primary_key=True, index=True)
	player_id = db.Column('player_id', db.Integer, db.ForeignKey('player.id'), nullable=False)
	song_id = db.Column('song_id', db.Integer, db.ForeignKey('song.id'), nullable=False)

	playtype = db.Column('playtype', db.String(8))
	playscore = db.Column('playscore', db.Integer)
	playrate = db.Column('playrate', db.Float)
	playclear = db.Column('playclear', db.Integer)
	playmiss = db.Column('playmiss', db.Integer)

class Player(db.Model):
	__tablename__ = 'player'
	id = db.Column('object_id', db.Integer, primary_key=True, index=True)
	time = db.Column('time', db.DateTime, nullable=False, default=sqlfuncs.now())
	records = db.relationship('PlayRecord', backref='player', lazy='select')

	iidxid = db.Column('iidxid', db.String(12))
	sppoint = db.Column('sppoint', db.Integer)
	dppoint = db.Column('dppoint', db.Integer)
	spclass = db.Column('spclass', db.Integer)
	dpclass = db.Column('dpclass', db.Integer)
	splevel = db.Column('splevel', db.Integer)	# need to calculate
	dplevel = db.Column('dplevel', db.Integer)	# need to calculate

	@property
	def is_expired(self):
		# 1 month = need to refresh data
		if self.expire_time:
			return (datetime.now() - self.time).total_seconds() >= 24*3600*30
		return False
