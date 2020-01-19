from django.core.management import BaseCommand
import iidxrank.models as models

class Command(BaseCommand):
    help = "copy song info to different difficulty."

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='song id to change')
        parser.add_argument('--type_to', type=str, help='song type to create')

    def handle(self, *args, **options):
        songid = options['id']
        songtypeto = options['type_to']
        song = models.Song.objects.filter(songid=songid).first()
        song.pk = None
        song.songtype = songtypeto
        song.save()
        print('done')
