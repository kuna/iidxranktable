# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-01-19 05:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iidxrank', '0014_auto_20180513_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='songid_iidxme',
            field=models.IntegerField(default=0),
        ),
    ]