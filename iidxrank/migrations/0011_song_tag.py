# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-13 15:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iidxrank', '0010_auto_20160713_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='tag',
            field=models.CharField(blank=True, default=b'', max_length=100),
        ),
    ]
