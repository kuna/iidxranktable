from django.core.management import BaseCommand
import iidxrank.models as models

class Command(BaseCommand):
    help = "update all song db from iidx.me"

    def handle(self, *args, **options):
        self.stdout.write("TEST")
        songs = models.Song.objects.filter(songtype="DPA", songlevel=12).all()[:10]
        for song in songs:
            print song.songtitle
