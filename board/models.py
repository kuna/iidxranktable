from __future__ import unicode_literals

from datetime import datetime, date
from django.db import models
from django.db.models import CASCADE
from django.utils.timezone import now

# this board will be used as guestboard/notice
class Board(models.Model):
  title = models.CharField(max_length=100)
  permission = models.IntegerField(default=0)   # 2: board only for admin

  def __unicode__(self):
    return self.title

class BoardPost(models.Model):
  time = models.DateTimeField(default=now)    # db updated time
  board = models.ForeignKey(Board, related_name="posts", on_delete=CASCADE, null=True)
  title = models.CharField(max_length=100)
  text = models.TextField()
  writer = models.CharField(max_length=200)
  tag = models.CharField(max_length=100, default="", blank=True)
  ip = models.CharField(max_length=100)
  attr = models.IntegerField(default=0)
  password = models.CharField(max_length=100)
  permission = models.IntegerField(default=0)

  def get_boardtitle(self):
    return self.board.title

  def __unicode__(self):
    return self.title

  def check_comment_exists(self):
    return self.comments.filter(parent=None).exists()

  def get_comments(self):
    return self.comments.filter(parent=None).order_by('-time').all()

class BoardComment(models.Model):
  time = models.DateTimeField(default=now)    # db updated time
  post = models.ForeignKey(BoardPost, related_name="comments", on_delete=CASCADE, null=True)
  parent = models.ForeignKey("self", related_name="childs", on_delete=CASCADE, null=True, blank=True)
  text = models.CharField(max_length=1000)
  writer = models.CharField(max_length=100)
  tag = models.CharField(max_length=100, default="", blank=True)
  ip = models.CharField(max_length=100)
  attr = models.IntegerField(default=0)
  password = models.CharField(max_length=100)

  def get_posttitle(self):
    return self.post.title

class BannedUser(models.Model):
  ip = models.CharField(max_length=100)

  def __unicode__(self):
    return self.ip

class BannedWord(models.Model):
  word = models.CharField(max_length=100)

  def __unicode__(self):
    return self.word
