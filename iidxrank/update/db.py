from sqlalchemy import Column, Integer, String, func, ForeignKey, Float, DateTime, UniqueConstraint 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
import os
import private

Base = declarative_base()

class RankTable(Base):
	__tablename__ = 'iidxrank_ranktable'
	id = Column(Integer, primary_key=True, index=True)
	time = Column('time', DateTime, nullable=False, default=func.now())		# db updated time
	category = relationship('RankCategory', backref='ranktable', lazy='select')

	tablename = Column('tablename', String(100))
	tabletitle = Column('tabletitle', String(100))
	level = Column('level', Integer)
	type = Column('type', String(100))
	copyright = Column('copyright', String(100))

	@property
	def songs(self):
		song_obj = []
		for category in self.category:
			song_obj = song_obj + category.songs
		return song_obj

	@property
	def unknownsongs(self):
		return Song.query\
			.filter(Song.songlevel == self.level)\
			.filter(Song.songtype.like(self.type + "%"))\
			.except_(Song.query.join(RankItem).join(RankCategory)\
				.filter(RankCategory.ranktable == self))\
			.all()

class RankCategory(Base):
	__tablename__ = 'iidxrank_rankcategory'
	id = Column(Integer, primary_key=True, index=True)
	rankitem = relationship('RankItem', backref='rankcategory')

	ranktable_id = Column(Integer, ForeignKey('iidxrank_ranktable.id'))
	categoryname = Column('categoryname', String(20))

	@property
	def songs(self):
		song_obj = []
		for rankitem in self.rankitem:
			x = rankitem.song
			if (x != None):
				song_obj.append(x)
		return song_obj

class RankItem(Base):
	__tablename__ = 'iidxrank_rankitem'
	id = Column(Integer, primary_key=True, index=True)
	song_id = Column(Integer, ForeignKey('iidxrank_song.id'))	# this cannot be null & can direct same song
	rankcategory_id = Column(Integer, ForeignKey('iidxrank_rankcategory.id'))

	info = Column('info', String(400))

class Song(Base):
	__tablename__ = 'iidxrank_song'
	__table_args__ = (UniqueConstraint('songid', 'songtype'), )
	id = Column(Integer, primary_key=True, index=True)
	playrecord = relationship('PlayRecord', backref='song')
	rankitem = relationship('RankItem', backref='song', lazy='select')

	songid = Column('songid', Integer)
	songtype = Column('songtype', String(8))		# dph/spa ...
	songtitle = Column('songtitle', String(40))
	songlevel = Column('songlevel', Integer)
	songnotes = Column('songnotes', Integer)

	# for calculating MCMC
	calclevel_easy = Column(Float)
	calcweight_easy = Column(Float)
	calclevel_normal = Column(Float)
	calcweight_normal = Column(Float)
	calclevel_hd = Column(Float)
	calcweight_hd = Column(Float)
	calclevel_exh = Column(Float)
	calcweight_exh = Column(Float)

class PlayRecord(Base):
	__tablename__ = 'iidxrank_playrecord'
	id = Column(Integer, primary_key=True, index=True)
	player_id = Column(Integer, ForeignKey('iidxrank_player.id'))
	song_id = Column(Integer, ForeignKey('iidxrank_song.id'))

	playscore = Column('playscore', Integer)
	playclear = Column('playclear', Integer)
	playmiss = Column('playmiss', Integer)

class Player(Base):
	__tablename__ = 'iidxrank_player'
	id = Column(Integer, primary_key=True, index=True)
	time = Column('time', DateTime, nullable=False, default=func.now())
	playrecord = relationship('PlayRecord', backref='player')

	iidxid = Column('iidxid', String(12))
	iidxmeid = Column('iidxmeid', String(12))
	iidxnick = Column('iidxnick', String(12))
	sppoint = Column('sppoint', Integer)
	dppoint = Column('dppoint', Integer)
	spclass = Column('spclass', Integer)
	dpclass = Column('dpclass', Integer)
	splevel = Column('splevel', Float)	# need to calculate
	dplevel = Column('dplevel', Float)	# need to calculate

	@property
	def is_expired(self):
		# 1 month = need to refresh data
		if self.expire_time:
			return (datetime.now() - self.time).total_seconds() >= 24*3600*30
		return False


"""
if (not os.path.exists("data.db")):
	open("data.db", "a").close()	# create empty file
engine = create_engine('sqlite:///data.db', convert_unicode=True)
"""
engine = create_engine(private.session_url, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.query = db_session.query_property()

# get db_session
def get_session():
	return db_session

# do commit
def commit():
	db_session.commit()

# do commit
# you may don't need to use this
def remove():
	db_session.remove()

# you shouldn't call it here - call it in django (migrate)
def init_db():
	raise Exception("Don't call this here!")
	Base.metadata.create_all(bind=engine)
