from django.core.management import BaseCommand
import iidxrank.models as models
import update.calculatedb

class Command(BaseCommand):
    help = """update song/user calculation level;
args:
initlevel = initalize song level
user [username] = only calculate [username]'s level"""

    def add_arguments(self, parser):
        parser.add_argument('--work')
        parser.add_argument('--init')#, action='store_true')

    def handle(self, *args, **options):
        # do initialization before DB calculation
        print '1. preparing before calculation ...'
        if (options['init'] == "song"):
            update.calculatedb.prepare_song_all()
        elif (options['init'] == "user"):
            update.calculatedb.prepare_user_all()
        elif (options['init'] == "all"):
            update.calculatedb.prepare_song_all()
            update.calculatedb.prepare_user_all()
        else:
            print '(skip initalization)'

        # main work: sigmoid
        print '2. calculation ...'
        if (options['work'] == "song"):
            update.calculatedb.calculate_song_all()
        elif (options['work'] == "user"):
            update.calculatedb.calculate_user_all()
        else:
            print '10 iteration of user/song of sigmoid model using MCMC method'
            for i in range(10):
                print '## iter: %d' % (i+1)
                update.calculatedb.calculate_user_all()     # user first!
                update.calculatedb.calculate_song_all()
