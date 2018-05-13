from django.core.management import BaseCommand
import iidxrank.models as models
import update.updatedb as updatedb
import update.parser_iidxme as iidxme

class Command(BaseCommand):
    help = "update all song db from iidx.me (or specific song number)"

    def add_arguments(self, parser):
        parser.add_argument('--num', type=int, help='specific song number of iidx.me to update')
        parser.add_argument('--set_version', type=int, help='specific version of added song (for default value)', default=99)

    def handle(self, *args, **options):
        #self.stdout.write("TEST")
        #songs = models.Song.objects.filter(songtype="DPA", songlevel=12).all()[:10]
        #for song in songs:
        #    print song.songtitle
        #print iidxme.parse_songs_http()
        if (options['set_version']):
            updatedb.VERSION = options['set_version']
        if (options['num']):
            updatedb.update_iidxme_song(options['num'])
        else:
            updatedb.update_iidxme()
