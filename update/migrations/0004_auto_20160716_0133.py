# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-15 16:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('update', '0003_songcalc_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='songcalc',
            name='song',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.Song'),
        ),
    ]