from django.core.management import BaseCommand
import iidxrank.models as models
import update.updatedb as updatedb
import update.parser_iidxme as iidxme

class Command(BaseCommand):
    help = "update all song db from iidx.me (or specific song number)"

    def add_arguments(self, parser):
        parser.add_argument('--num', type=int, help='specific song number of iidx.me to update')
        parser.add_argument('--set_version', type=int, help='specific version of added song')
        parser.add_argument('--username', type=str, default='delmitz')
        parser.add_argument('--test', type=int, help='only for test (not actually update record)')

    def handle(self, *args, **options):
        #self.stdout.write("TEST")
        #songs = models.Song.objects.filter(songtype="DPA", songlevel=12).all()[:10]
        #for song in songs:
        #    print song.songtitle
        #print iidxme.parse_songs_http()
        usrname = options['username']
        if (options['set_version']):
            updatedb.VERSION = options['set_version']
        if (options['test']):
            updatedb.TEST = options['test']
        if (options['num']):
            updatedb.update_iidxme_song(options['num'])
        else:
            updatedb.update_iidxme(usrname, options['set_version'])
