# -*- coding: utf-8 -*-
# fix iidx.me song id from iidx.me database

from django.core.management import BaseCommand
import iidxrank.models as models

class Command(BaseCommand):
    help = """this fixes iidx.me song id"""

    def handle(self, *args, **options):
        pass
