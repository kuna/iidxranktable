# -*- coding: utf-8 -*-
# fix iidx.me song id from iidx.me database

from django.core.management import BaseCommand
import iidxrank.models as models
import update.parser_iidxme as iidxme
import copy



def mark_ids(songs, songdata):
    musicdata = songdata['musicdata']
    song_remained = []
    for song in songs:
        song_detected= False
        for music in musicdata:
            if (song.songtitle == music['data']['title']):
                song.songid = music['data']['id']
                song_detected = True
                break
        if (not song_detected):
            song_remained.append(song)
    return song_remained



class Command(BaseCommand):
    help = """this fixes iidx.me song id"""

    def handle(self, *args, **options):
        print 'parsing iidx.me song info ...'
        songdata_lv10sp = iidxme.parse_iidxme_http('http://iidx.me/delmitz/sp/level/10')
        songdata_lv11sp = iidxme.parse_iidxme_http('http://iidx.me/delmitz/sp/level/11')
        songdata_lv12sp = iidxme.parse_iidxme_http('http://iidx.me/delmitz/sp/level/12')
        songdata_lv10dp = iidxme.parse_iidxme_http('http://iidx.me/delmitz/dp/level/10')
        songdata_lv11dp = iidxme.parse_iidxme_http('http://iidx.me/delmitz/dp/level/11')
        songdata_lv12dp = iidxme.parse_iidxme_http('http://iidx.me/delmitz/dp/level/12')

        songs = models.Song.objects.all()
        songs_original = copy.copy(songs)
        print 'total song objects: %d' % len(songs)

        songs = mark_ids(songs, songdata_lv10sp)
        print 'remains: %d' % len(songs)
        songs = mark_ids(songs, songdata_lv11sp)
        print 'remains: %d' % len(songs)
        songs = mark_ids(songs, songdata_lv12sp)
        print 'remains: %d' % len(songs)
        songs = mark_ids(songs, songdata_lv10dp)
        print 'remains: %d' % len(songs)
        songs = mark_ids(songs, songdata_lv11dp)
        print 'remains: %d' % len(songs)
        songs = mark_ids(songs, songdata_lv12dp)
        print 'remains: %d' % len(songs)

        print 'done, remaining list:'
        for song in songs:
            print '%s / %d / %s' % (song.songtitle, song.songlevel, song.songtype)

        for song in songs_original:
            if (song in songs):
                continue
            song.save()
        print 'DB saving done'
