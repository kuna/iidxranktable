from __future__ import absolute_import

import os

from celery import Celery
from celery.utils.log import get_task_logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.conf import settings  # noqa

app = Celery('update')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# before prepare models .. DONT!
#import django
#django.setup()


import update.updatedb
import update.updateuser
import update.calculatedb

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task(name="update_user")
def update_user(iidxmeid):
    print('User update request: %s' % iidxmeid)
    update.updateuser.update_playrecord(iidxmeid)
    print('Calculating user level')
    update.calculatedb.calculate_user_id(iidxmeid)
    print('Done!')


# some periodic tasks
@app.periodic_task(run_every=(crontab(hour='*/24')), name="update_song", ignore_result=True)
def song_update():
    update.updatedb.update_iidxme()
