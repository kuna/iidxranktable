from django.core.management import BaseCommand
import iidxrank.models as models
import update.updatedb as updatedb

class Command(BaseCommand):
    help = "update all song db from remywiki"

    def add_arguments(self, parser):
        parser.add_argument('--set_version', type=int, help='specific version of song version')
        parser.add_argument('--test', type=int, help='only for test (not actually update record)')

    def handle(self, *args, **options):
        version = -1
        if (options['set_version']):
            version = options['set_version']
        if (options['test']):
            updatedb.TEST = options['test']
        updatedb.update_from_remywiki(version)
