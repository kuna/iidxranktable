# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-05-13 03:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_auto_20180513_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boardpost',
            name='text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='boardpost',
            name='writer',
            field=models.CharField(max_length=200),
        ),
    ]
