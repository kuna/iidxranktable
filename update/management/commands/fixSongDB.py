# -*- coding: utf-8 -*-
# this fixes incorrect song DB data
# - generate SPL difficulty if song is leggendaries
# - generates song tag data

from django.core.management import BaseCommand
import iidxrank.models as models

class Command(BaseCommand):
    help = """this fixes incorrect song DB data (tag / SPL difficulty)"""

    def handle(self, *args, **options):
        songs = models.Song.objects.all()
        i = 0
        for song in songs:
            if (song.songtitle.endswith(u'†') or song.songtitle.endswith(u'†LEGGENDARIA')):
                if (song.songtype[:2] == "SP"):
                    song.songtype = "SPL"
                elif (song.songtype[:2] == "DP"):
                    song.songtype = "DPL"
                else:
                    print("WARNING: %s song has incorrect difficulty" % song.songtitle)
                song.tag = song.songtitle.split(u'†')[0]
            else:
                song.tag = song.songtitle
            i += 1
            print "%d / %d" % (i, len(songs))
            song.save()
