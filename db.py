from sqlalchemy import Column, Integer, String, func, ForeignKey, Float, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
import os

Base = declarative_base()

class RankTable(Base):
	__tablename__ = 'ranktable'
	id = Column(Integer, primary_key=True, index=True)
	category = relationship('RankCategory', backref='ranktable', lazy='select')

	tablename = Column('tablename', String(100))

class RankCategory(Base):
	__tablename__ = 'rankcategory'
	id = Column(Integer, primary_key=True, index=True)
	rankitem = relationship('RankItem', backref='category', lazy='select')

	table_id = Column(Integer, ForeignKey('ranktable.id'))
	categoryname = Column('categoryname', String(20))

class RankItem(Base):
	__tablename__ = 'rankitem'
	id = Column(Integer, primary_key=True, index=True)
	song_id = Column(Integer, ForeignKey('song.id'))	# this cannot be null & can direct same song
	category_id = Column(Integer, ForeignKey('rankcategory.id'))

	songtype = Column('songtype', String(8))		# dph/spa ...
	songtitle = Column('songtitle', String(40))

class Song(Base):
	__tablename__ = 'song'
	id = Column(Integer, primary_key=True, index=True)
	playrecord = relationship('PlayRecord', backref='song', lazy='select')
	rankitem = relationship('RankItem', backref='song', lazy='select')

	songid = Column('songid', Integer)
	songtype = Column('songtype', String(8))		# dph/spa ...
	songtitle = Column('songtitle', String(40))
	songlevel = Column('songlevel', Integer)
	songnotes = Column('songnotes', Integer)

class PlayRecord(Base):
	__tablename__ = 'playrecord'
	id = Column(Integer, primary_key=True, index=True)
	player_id = Column(Integer, ForeignKey('player.id'))
	song_id = Column(Integer, ForeignKey('song.id'))

	playtype = Column('playtype', String(8))	# SPN/SPH/SPA ...
	playscore = Column('playscore', Integer)
	playrate = Column('playrate', Float)
	playclear = Column('playclear', Integer)
	playmiss = Column('playmiss', Integer)

class Player(Base):
	__tablename__ = 'player'
	id = Column(Integer, primary_key=True, index=True)
	time = Column('time', DateTime, nullable=False, default=func.now())
	playrecord = relationship('PlayRecord', backref='player', lazy='select')

	iidxid = Column('iidxid', String(12))
	sppoint = Column('sppoint', Integer)
	dppoint = Column('dppoint', Integer)
	spclass = Column('spclass', Integer)
	dpclass = Column('dpclass', Integer)
	splevel = Column('splevel', Integer)	# need to calculate
	dplevel = Column('dplevel', Integer)	# need to calculate

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