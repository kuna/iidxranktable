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
			'calclevel': round(song.calclevel_hd, 2),
			'calcweight': round(song.calcweight_hd, 2),
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
