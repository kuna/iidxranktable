from __future__ import unicode_literals

from django.db import models
import iidxrank.models

# User / UserRecord / SongCalc.

class PlayerCalc(models.Model):
    player = models.OneToOneField(iidxrank.models.Player)
    tag = models.CharField(max_length=20)

    valid = models.IntegerField(default=0)  # if no fail, then it's invalid; can't calculate
    sp_l = models.FloatField(default=0)
    sp_w = models.FloatField(default=0)
    dp_l = models.FloatField(default=0)
    dp_w = models.FloatField(default=0)

class SongCalc(models.Model):
    song = models.OneToOneField(iidxrank.models.Player)
    tag = models.CharField(max_length=20)

    valid = models.IntegerField(default=0)  # if no fail, then it's invalid; can't calculate
    ez_l = models.FloatField(default=0)
    ez_w = models.FloatField(default=0)
    nm_l = models.FloatField(default=0)
    nm_w = models.FloatField(default=0)
    hd_l = models.FloatField(default=0)
    hd_w = models.FloatField(default=0)
    ex_l = models.FloatField(default=0)
    ex_w = models.FloatField(default=0)
    fc_l = models.FloatField(default=0)
    fc_w = models.FloatField(default=0)

    score_avg = models.FloatField(default=0)
