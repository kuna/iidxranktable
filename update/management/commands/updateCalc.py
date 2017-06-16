from django.core.management import BaseCommand
import iidxrank.models as models
import update.calculatedb

class Command(BaseCommand):
    help = """update song/user calculation level"""

    def handle(self, *args, **options):
        print '10 iteration of user/song of sigmoid model using MCMC method'
        for i in range(10):
            print '## iter: %d' % (i+1)
            update.calculatedb.update_song_all()
            update.calculatedb.update_user_all()
