from django.core.management import BaseCommand
import update.calcdump as calcdump
import json

class Command(BaseCommand):
    help = """dump song/user level/clear info into json file for calculation"""

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('--action', default='dump', help='dump / load')

    def handle(self, *args, **options):
        if (options['action'] == 'dump'):
            self.dump(options['path'])
        elif (options['action'] == 'load'):
            self.load(options['path'])
        else:
            raise Exception('invalid action')

    def dump(self, path):
        j = calcdump.dump_json()
        with open(path, 'w') as f:
            print 'output file: ', path
            json.dump(j, f)

    def load(self, path):
        with open(path, 'r') as f:
            j = json.load(f)
        calcdump.load_json(j)
        print 'loading done.'
