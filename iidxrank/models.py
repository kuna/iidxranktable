# lets refer: https://docs.djangoproject.com/en/1.9/intro/tutorial07/
# http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/

from datetime import datetime
from django.db import models	# whether to use django?
from django.db.models import CASCADE
from django.utils.timezone import now

class Song(models.Model):
	songid = models.IntegerField(default=0)
	songtype = models.CharField(max_length=8)		# dph/spa ...
	songtitle = models.CharField(max_length=100)
	songlevel = models.IntegerField(default=0)
	songnotes = models.IntegerField(default=0)

	# for calculating MCMC ..?
	calclevel = models.FloatField(default=0)
	calcweight = models.FloatField(default=0)

	def __unicode__(self):
		return self.songtitle + "/" + str(self.songlevel) + "/" + self.songtype

	class Meta:
		unique_together = ['songid', 'songtype',]

class Player(models.Model):
	time = models.DateTimeField(auto_now=True)

	iidxid = models.CharField(max_length=12)
	iidxmeid = models.CharField(max_length=12)
	iidxnick = models.CharField(max_length=12)
	sppoint = models.IntegerField(default=0)
	dppoint = models.IntegerField(default=0)
	spclass = models.IntegerField(default=0)
	dpclass = models.IntegerField(default=0)
	splevel = models.FloatField(default=0)	# need to calculate
	dplevel = models.FloatField(default=0)	# need to calculate

	def __unicode__(self):
		return self.iidxnick + "/" + str(self.spclass) + "/" + str(self.dpclass)

	@property
	def is_expired(self):
		# 1 month = need to refresh data
		if self.expire_time:
			return (datetime.now() - self.time).total_seconds() >= 24*3600*30
		return False

class PlayRecord(models.Model):
	player = models.ForeignKey(Player, on_delete=CASCADE)
	song = models.ForeignKey(Song, on_delete=CASCADE)
	playscore = models.IntegerField(default=0)
	playclear = models.IntegerField(default=0)
	playmiss = models.IntegerField(default=0)


class RankTable(models.Model):
	time = models.DateTimeField(default=now)		# db updated time
	tablename = models.CharField(max_length=100)
	tabletitle = models.CharField(max_length=100)
	level = models.IntegerField(default=0)
	type = models.CharField(max_length=100)
	copyright = models.CharField(max_length=100)

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

	def __unicode__(self):
		return self.tabletitle

class RankCategory(models.Model):
	ranktable = models.ForeignKey(RankTable, on_delete=models.CASCADE)
	categoryname = models.CharField(max_length=20)

	def get_tabletitle(obj):
		return obj.ranktable.tabletitle

	@property
	def songs(self):
		song_obj = []
		for rankitem in self.rankitem:
			x = rankitem.song
			if (x != None):
				song_obj.append(x)
		return song_obj

	def __unicode__(self):
		return self.get_tabletitle() + "/" + self.categoryname

# CLAIM: this does same work as board category!
class RankItem(models.Model):
	rankcategory = models.ForeignKey(RankCategory, on_delete=models.CASCADE)
	song = models.ForeignKey(Song, null=True, blank=True)	# this cannot be null & can direct same song
	info = models.CharField(max_length=400)		# unique string, maybe...

	def get_songtitle(obj):
		return obj.song.songtitle
	def get_songlevel(obj):
		return obj.song.songlevel
	def get_songtype(obj):
		return obj.song.songtype
	def get_categoryname(obj):
		return obj.rankcategory.categoryname


# newly added comment system
class Comment(models.Model):
	time = models.DateTimeField(default=now)		# db updated time
	rankitem = models.ForeignKey(RankItem, on_delete=CASCADE)
	text = models.CharField(max_length=1000)
	score = models.IntegerField(default=0)	# 99: just a comment
	writer = models.CharField(max_length=100)
	ip = models.CharField(max_length=100)
	attr = models.IntegerField(default=0)	# 0: normal, 1: hide, 2: admin

# this board will be used as guestboard/notice
class Board(models.Model):
	title = models.CharField(max_length=100)

	def __unicode__(self):
		return self.title

class BoardComment(models.Model):
	time = models.DateTimeField(default=now)		# db updated time
	board = models.ForeignKey(Board, on_delete=CASCADE)
	text = models.CharField(max_length=1000)
	writer = models.CharField(max_length=100)
	ip = models.CharField(max_length=100)
	attr = models.IntegerField(default=0)

	def get_boardtitle(self):
		return self.board.title

class BannedUser(models.Model):
	ip = models.CharField(max_length=100)

# depreciated (SQLAlchemy part)
def init_db():
	#if (not os.path.exists("data.db")):
	#	open("data.db", "a").close()	# create empty file
	#engine = create_engine('sqlite:///data.db', convert_unicode=True)
	db_session = scoped_session(sessionmaker(bind=engine))
	Base.query = db_session.query_property()
	Base.metadata.create_all(bind=engine)
	return db_session
