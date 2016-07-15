# lets refer: https://docs.djangoproject.com/en/1.9/intro/tutorial07/
# http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/

from datetime import datetime, date
from django.db import models    # whether to use django?
from django.db.models import CASCADE
from django.utils.timezone import now

class Song(models.Model):
    songid = models.IntegerField(default=0)
    songtype = models.CharField(max_length=8)       # dph/spa ...
    songtitle = models.CharField(max_length=100)
    songlevel = models.IntegerField(default=0)
    songnotes = models.IntegerField(default=0)
    version = models.CharField(max_length=20)

    # TODO: add iidx song english name
    #songtitle_eng = models.CharField(max_length=100)

    # for calculating MCMC ..?
    calclevel_easy = models.FloatField(default=0)
    calcweight_easy = models.FloatField(default=0)
    calclevel_normal = models.FloatField(default=0)
    calcweight_normal = models.FloatField(default=0)
    calclevel_hd = models.FloatField(default=0)
    calcweight_hd = models.FloatField(default=0)
    calclevel_exh = models.FloatField(default=0)
    calcweight_exh = models.FloatField(default=0)

    tag = models.CharField(default="", max_length=100, blank=True)

    def __unicode__(self):
        return self.songtitle + "/" + str(self.songlevel) + "/" + self.songtype

    def get_tags(self):
        if (self.tag == ""):
            return []
        else:
            return self.tag.split(",")

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

    splevel = models.FloatField(default=0)  # need to calculate
    dplevel = models.FloatField(default=0)  # need to calculate

    def __unicode__(self):
        return self.iidxnick + "/" + str(self.spclass) + "/" + str(self.dpclass)

    def iidxmeid_private(self):
        return self.iidxmeid[:1] + "*"*(len(self.iidxmeid)-2) + self.iidxmeid[-1:]
    def iidxnick_private(self):
        return self.iidxnick[:1] + "*"*(len(self.iidxnick)-2) + self.iidxnick[-1:]
    def isRefreshable(self):
        #print (now() - self.time).total_seconds() / 60 / 60 / 24
        return ((now() - self.time).total_seconds() / 60 / 60 / 24) >= 1

class PlayRecord(models.Model):
    # MUST use db_index for performance
    player = models.ForeignKey(Player, on_delete=CASCADE, db_index=True)
    song = models.ForeignKey(Song, on_delete=CASCADE, db_index=True)
    playscore = models.IntegerField(default=0, null=True)
    playclear = models.IntegerField(default=0)
    playmiss = models.IntegerField(default=0, null=True)

    def _getScoreCalculated(self):
        if (self.playclear == 3):
            return self.song.songcalc.ez_l
        if (self.playclear == 4):
            return self.song.songcalc.nm_l
        if (self.playclear == 5):
            return self.song.songcalc.hd_l
        if (self.playclear == 6):
            return self.song.songcalc.ex_l
        else:
            return 0
    getScoreCalculated = property(_getScoreCalculated)

class RankTable(models.Model):
    time = models.DateTimeField(default=now)        # db updated time
    tablename = models.CharField(max_length=100)
    tabletitle = models.CharField(max_length=100)
    tabletitlehtml = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    type = models.CharField(max_length=100)
    copyright = models.CharField(max_length=100)

    def getTitleHTML(self):
        if (self.tabletitlehtml == ""):
            return self.tabletitle
        else:
            return self.tabletitlehtml

    def __unicode__(self):
        return self.tabletitle

class RankCategory(models.Model):
    ranktable = models.ForeignKey(RankTable, on_delete=models.CASCADE)
    categoryname = models.CharField(max_length=20)
    categorytype = models.IntegerField(default=0)
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
    song = models.ForeignKey(Song, null=True, blank=True)   # this cannot be null & can direct same song
    info = models.CharField(max_length=400)     # unique string, maybe...

    def get_songtitle(obj):
        return obj.song.songtitle
    def get_songlevel(obj):
        return obj.song.songlevel
    def get_ranktablename(obj):
        return obj.rankcategory.ranktable.tablename
    def get_categoryname(obj):
        return obj.rankcategory.categoryname


