from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import models
import iidx

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
			'calclevel': round(song.calclevel, 2),
			'calcweight': round(song.calcweight, 2),
		})
	return song_array

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
			'iidxnick': user.iidxnick_private(),
			'spdan': iidx.getdanstring(user.spclass),
			'dpdan': iidx.getdanstring(user.dpclass),
			'splevel': round(user.splevel, 2),
			'dplevel': round(user.dplevel, 2),
			'sprank': models.Player.objects.filter(splevel__gt=user.splevel).count()+1,
			'dprank': models.Player.objects.filter(dplevel__gt=user.dplevel).count()+1,
		})
	return JsonResponse({'status':'success', 'users': user_array})