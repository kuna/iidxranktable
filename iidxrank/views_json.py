#-*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import models
import iidx
import recommend

def createSonginfoFromModel(songs):
  song_array = []
  for song in songs:
    cates = []
    for rank in song.rankitem_set.all():
      cates.append(rank.rankcategory.categoryname)
    song_array.append({
      'songtitle': song.songtitle,
      'songdiff': song.songtype[-1:],
      'songtype': song.songtype,
      'songlevel': song.songlevel,
      'series': song.version,
      'categories': cates,
      'calclevel_easy': round(song.calclevel_easy, 2),
      'calcweight_easy': round(song.calcweight_easy, 2),
      'calclevel_normal': round(song.calclevel_normal, 2),
      'calcweight_normal': round(song.calcweight_normal, 2),
      'calclevel_hd': round(song.calclevel_hd, 2),
      'calcweight_hd': round(song.calcweight_hd, 2),
      'calclevel_exh': round(song.calclevel_exh, 2),
      'calcweight_exh': round(song.calcweight_exh, 2),
    })
  return song_array

def getLevel(lv):
  return round(lv, 2)
##############################################################

def json_level(request, type, level):
  songs = models.Song.objects.filter(songtype__istartswith=type, songlevel=level).order_by('songtitle').all()
  return JsonResponse({'status':'success', 'songs': createSonginfoFromModel(songs)})

def json_series(request, type, series):
  songs = models.Song.objects.filter(songtype=type, version=series).order_by('songtitle').all()
  return JsonResponse({'status':'success', 'songs': createSonginfoFromModel(songs)})

def json_user(request):
  user_array = []
  for user in models.Player.objects.all():
    user_array.append({
      'iidxid': user.iidxid,
      'iidxmeid': user.iidxmeid_private(),
      'iidxnick': user.iidxnick,
      'spdan': iidx.getdanstring(user.spclass),
      'dpdan': iidx.getdanstring(user.dpclass),
      'splevel': getLevel(user.splevel),
      'dplevel': getLevel(user.dplevel),
      'sprank': models.Player.objects.filter(splevel__gt=user.splevel).count()+1,
      'dprank': models.Player.objects.filter(dplevel__gt=user.dplevel).count()+1,
    })
  return JsonResponse({'status':'success', 'users': user_array})

def json_recommend(request, username, type, level=-1):
  player = models.Player.objects.filter(iidxmeid=username).first()
  if (player == None):
    return JsonResponse({'status': 'not existing user', 'recommends': []})
  recommends = recommend.findRecommend_fast(player, type, level)
  return JsonResponse({'status': 'success', 'recommends': recommends})


def json_rankedit(request):
  # staff / admin only
  if not request.user.is_staff:
    return JsonResponse({'message': 'access denied'})

  # in case of POST? -> return JSON result
  if (request.method == "POST"):
    if (request.POST['action'] == 'song'):
      pk = int(request.POST['id'])
      obj = models.RankItem.objects.filter(id=pk).first()
      if (obj == None):
        return JsonResponse({'message': 'wrong object id'})
      pk_cate = int(request.POST['categoryid'])
      if (pk_cate == -1):
        obj.remove()
      else:
        obj_cate = models.RankCategory.objects.filter(id=pk_cate).first()
        if (obj_cate == None):
          return JsonResponse({'message': 'wrong category id'})
        obj.title = request.POST['title']
        obj.tag = request.POST['tag']
        obj.category = obj_cate;
        obj.save();
      return JsonResponse({'message': 'successfully done'})
    elif (request.POST['action'] == 'category'):
      pk = int(request.POST['id'])
      obj_cate = models.RankCategory.objects.filter(id=obj_cate).first()
      if (obj_cate == None):
        return JsonResponse({'message': 'wrong category id'})
      obj_cate.title = request.POST['title']
      obj_cate.categorytype = int(request.POST(['categorytype']))
      obj_cate.sortindex = float(request.POST(['sortindex']))
      obj_cate.save()
      return JsonResponse({'message': 'successfully done'})
    elif (request.POST['action'] == 'table'):
      return JsonResponse({'message': 'not implemented'})
    elif (request.POST['action'] == 'songcategory'):
      pk = int(request.POST['id'])
      obj = models.RankItem.objects.filter(id=pk).first()
      pk_cate = int(request.POST['category'])
      if (pk_cate == -1):
        obj_cate = None
      else:
        obj_cate = models.RankCategory.objects.filter(id=pk_cate).first()
        if (obj_cate == None):
          return JsonResponse({'message': 'wrong category id'})
      if (obj == None):
        # create rankitem object
        # in case of none-created rankitem
        # if even songid doesn't exists,
        # then - serious error.
        songpk = int(request.POST['songid'])
        obj_song = models.Song.objects.filter(id=songpk).first()
        if (obj_song == None):
          return JsonResponse({'messasge': 'wrong object id'})
        else:
          obj = models.RankItem.objects.create(
                  rankcategory = obj_cate,
                  song = obj_song,
                  info = ''
                  )
      else:
        # delete or modify songitem's category
        if (obj_cate == None):
          print 'deleted'
          obj.delete()
        else:
          print '%s to %s' % (obj.song.songtitle, obj_cate.categoryname)
          obj.rankcategory = obj_cate
          obj.save()
      return JsonResponse({'message': 'successfully done'})
  else:
    return JsonResponse({'message': 'invalid access'})
