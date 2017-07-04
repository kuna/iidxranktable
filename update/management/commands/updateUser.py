from django.core.management import BaseCommand
import iidxrank.models as models
import update.updateuser

class Command(BaseCommand):
    help = "update all song db from iidx.me"

    def handle(self, *args, **options):
        #print 'updating users ...'
        #update.updateuser.update_user()
        print 'updating play records ...'
        update.updateuser.update_playrecord_all()
