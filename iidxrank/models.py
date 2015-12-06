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
	version = models.CharField(max_length=20)

	# TODO: add iidx song series & english name
	#series = models.IntegerField(default=0)
	#songtitle_eng = models.CharField(max_length=100)

	# for calculating MCMC ..?
	calclevel = models.FloatField(default=0)
	calcweight = models.FloatField(default=0)

	def __unicode__(self):
		return self.songtitle + "/" + str(self.songlevel) + "/" + self.songtype

	class Meta:
		unique_together = ['songid', 'songtype',]

class Player(models.Model):
	time = models.DateTimeField(auto_now=True)

	iidxid = models.CharField(max_length=20)
	iidxmeid = models.CharField(max_length=20)
	iidxnick = models.CharField(max_length=20)
	sppoint = models.IntegerField(default=0)
	dppoint = models.IntegerField(default=0)
	spclass = models.IntegerField(default=0)
	dpclass = models.IntegerField(default=0)
	splevel = models.FloatField(default=0)	# need to calculate
	dplevel = models.FloatField(default=0)	# need to calculate

	def __unicode__(self):
		return self.iidxnick + "/" + str(self.spclass) + "/" + str(self.dpclass)

	def iidxmeid_private(self):
		return self.iidxmeid[:1] + "*"*(len(self.iidxmeid)-2) + self.iidxmeid[-1:]

	def iidxnick_private(self):
		return self.iidxnick[:1] + "*"*(len(self.iidxnick)-2) + self.iidxnick[-1:]

class PlayRecord(models.Model):
	# MUST use db_index for performance
	player = models.ForeignKey(Player, on_delete=CASCADE, db_index=True)
	song = models.ForeignKey(Song, on_delete=CASCADE, db_index=True)
	playscore = models.IntegerField(default=0, null=True)
	playclear = models.IntegerField(default=0)
	playmiss = models.IntegerField(default=0, null=True)


class RankTable(models.Model):
	time = models.DateTimeField(default=now)		# db updated time
	tablename = models.CharField(max_length=100)
	tabletitle = models.CharField(max_length=100)
	level = models.IntegerField(default=0)
	type = models.CharField(max_length=100)
	copyright = models.CharField(max_length=100)

	def __unicode__(self):
		return self.tabletitle

class RankCategory(models.Model):
	ranktable = models.ForeignKey(RankTable, on_delete=models.CASCADE)
	categoryname = models.CharField(max_length=20)
	sortindex = models.FloatField(default=None, null=True, blank=True)

	def get_sortindex(self):
		if (self.sortindex):
			return self.sortindex
		else:
			import re
			decimal = re.sub(r'[^0-9.]+', '', self.categoryname)
			if (decimal == ""):
				decimal = "0"
			return float(decimal)
	def get_tabletitle(obj):
		return obj.ranktable.tabletitle

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
	def get_ranktablename(obj):
		return obj.rankcategory.ranktable.tablename
	def get_categoryname(obj):
		return obj.rankcategory.categoryname


# newly added comment system
class SongComment(models.Model):
	time = models.DateTimeField(default=now)		# db updated time
	# we'd better to identify song with: ranktable, song
	ranktable = models.ForeignKey(RankTable, on_delete=CASCADE)
	song = models.ForeignKey(Song, null=True, blank=True)

	text = models.CharField(max_length=1000)
	score = models.IntegerField(default=0)	# 99: just a comment
	writer = models.CharField(max_length=100)
	ip = models.CharField(max_length=100)
	attr = models.IntegerField(default=0)	# 0: normal, 1: hide, 2: admin
	password = models.CharField(max_length=100)

	def ip_public(self):
		return '.'.join(self.ip.split('.')[:2])
	def get_songinfo(self):
		return '%s / %s / %d' % (self.song.songtitle, self.song.songtype, self.song.songlevel)
	def get_ranktableinfo(self):
		return self.ranktable.tabletitle
	def get_rankitem(self):
		return RankItem.objects.filter(rankcategory__ranktable=self.ranktable, song=self.song).first()
	def get_rankcategory(self):
		rankitem = self.get_rankitem()
		if (rankitem):
			return rankitem.rankcategory
		else:
			return None

# this board will be used as guestboard/notice
class Board(models.Model):
	title = models.CharField(max_length=100)
	permission = models.IntegerField(default=0)		# 2: board only for admin

	def __unicode__(self):
		return self.title

class BoardComment(models.Model):
	time = models.DateTimeField(default=now)		# db updated time
	board = models.ForeignKey(Board, on_delete=CASCADE)
	text = models.CharField(max_length=1000)
	writer = models.CharField(max_length=100)
	ip = models.CharField(max_length=100)
	attr = models.IntegerField(default=0)
	password = models.CharField(max_length=100)

	def get_boardtitle(self):
		return self.board.title

class BannedUser(models.Model):
	ip = models.CharField(max_length=100)

	def __unicode__(self):
		return self.ip
