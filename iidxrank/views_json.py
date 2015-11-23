from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import models

def createSonginfoFromModel(songs):
	song_array = []
	for song in songs:
		cates = []
		for rank in song.rankitem_set.all():
			cates.append(rank.rankcategory.categoryname)
		song_array.append({
			'songtitle': song.songtitle,
			'songdiff': song.songtype[-1:],
			'songlevel': song.songlevel,
			'categories': cates,
		})
	return song_array

def json_level(request, type, level):
	songs = models.Song.objects.filter(songtype__icontains=type, songlevel=level).all()
	return JsonResponse({'status':'success', 'songs': createSonginfoFromModel(songs)})

def json_series(request, type, series):
	songs = models.Song.objects.filter(songtype=type, version=series).all()
	return JsonResponse({'status':'success', 'songs': createSonginfoFromModel(songs)})
