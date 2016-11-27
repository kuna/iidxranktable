from django.core.management import BaseCommand
import iidxrank.models as models
import update.updatedb as updatedb
import update.parser_iidxme as iidxme

class Command(BaseCommand):
    help = "update all song db from iidx.me"

    def handle(self, *args, **options):
        #self.stdout.write("TEST")
        #songs = models.Song.objects.filter(songtype="DPA", songlevel=12).all()[:10]
        #for song in songs:
        #    print song.songtitle
        updatedb.update_iidxme()
        #print iidxme.parse_songs_http()
