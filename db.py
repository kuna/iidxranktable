from sqlalchemy import Column, Integer, String, func
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
import os

Base = declarative_base()

class RankTable(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	category = db.relationship('RankCategory', backref='ranktable', lazy='select')

	tablename = db.Column('tablename', db.String(100))

class RankCategory(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	rankitem = db.relationship('RankItem', backref='category', lazy='select')

	table_id = db.Column(db.Integer, db.ForeignKey('rank_table.id'))
	categoryname = db.Column('categoryname', db.String(20))

class RankItem(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	song_id = db.Column(db.Integer, db.ForeignKey('song.id'))	# this cannot be null & can direct same song
	category_id = db.Column(db.Integer, db.ForeignKey('rank_category.id'))

	songtype = db.Column('songtype', db.String(8))		# dph/spa ...
	songtitle = db.Column('songtitle', db.String(40))

class Song(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	playrecord = db.relationship('PlayRecord', backref='song', lazy='select')
	rankitem = db.relationship('RankItem', backref='song', lazy='select')

	songid = db.Column('songid', db.Integer)
	songtype = db.Column('songtype', db.String(8))		# dph/spa ...
	songtitle = db.Column('songtitle', db.String(40))
	songlevel = db.Column('songlevel', db.Integer)
	songnotes = db.Column('songnotes', db.Integer)

class PlayRecord(db.Model):
	__tablename__ = 'play'
	id = db.Column(db.Integer, primary_key=True, index=True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	song_id = db.Column(db.Integer, db.ForeignKey('song.id'))

	playtype = db.Column('playtype', db.String(8))	# SPN/SPH/SPA ...
	playscore = db.Column('playscore', db.Integer)
	playrate = db.Column('playrate', db.Float)
	playclear = db.Column('playclear', db.Integer)
	playmiss = db.Column('playmiss', db.Integer)

class Player(db.Model):
	__tablename__ = 'player'
	id = db.Column(db.Integer, primary_key=True, index=True)
	time = db.Column('time', db.DateTime, nullable=False, default=func.now())
	playrecord = db.relationship('PlayRecord', backref='player', lazy='select')

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


def init_db():
	if (not os.path.exists("data.db")):
		open("data.db", "a").close()	# create empty file
	engine = create_engine('sqlite:///data.db', convert_unicode=True)
	db_session = scoped_session(sessionmaker(autocommit=False,
	                                         autoflush=False,
	                                         bind=engine))
	Base.query = db_session.query_property()
	Base.metadata.create_all(bind=engine)
	return db_session