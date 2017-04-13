# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-04-13 07:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('iidxrank', '0011_song_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
