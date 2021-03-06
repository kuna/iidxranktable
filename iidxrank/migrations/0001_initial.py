# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-06 18:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BannedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BannedWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('permission', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='BoardComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('text', models.CharField(max_length=1000)),
                ('writer', models.CharField(max_length=100)),
                ('ip', models.CharField(max_length=100)),
                ('attr', models.IntegerField(default=0)),
                ('password', models.CharField(max_length=100)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.Board')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now=True)),
                ('iidxid', models.CharField(max_length=20)),
                ('iidxmeid', models.CharField(max_length=20)),
                ('iidxnick', models.CharField(max_length=20)),
                ('sppoint', models.IntegerField(default=0)),
                ('dppoint', models.IntegerField(default=0)),
                ('spclass', models.IntegerField(default=0)),
                ('dpclass', models.IntegerField(default=0)),
                ('splevel', models.FloatField(default=0)),
                ('dplevel', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PlayRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playscore', models.IntegerField(default=0, null=True)),
                ('playclear', models.IntegerField(default=0)),
                ('playmiss', models.IntegerField(default=0, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.Player')),
            ],
        ),
        migrations.CreateModel(
            name='RankCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoryname', models.CharField(max_length=20)),
                ('categorytype', models.IntegerField(default=0)),
                ('sortindex', models.FloatField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RankItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=400)),
                ('rankcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.RankCategory')),
            ],
        ),
        migrations.CreateModel(
            name='RankTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('tablename', models.CharField(max_length=100)),
                ('tabletitle', models.CharField(max_length=100)),
                ('tabletitlehtml', models.CharField(max_length=200)),
                ('level', models.IntegerField(default=0)),
                ('type', models.CharField(max_length=100)),
                ('copyright', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('songid', models.IntegerField(default=0)),
                ('songtype', models.CharField(max_length=8)),
                ('songtitle', models.CharField(max_length=100)),
                ('songlevel', models.IntegerField(default=0)),
                ('songnotes', models.IntegerField(default=0)),
                ('version', models.CharField(max_length=20)),
                ('calclevel_easy', models.FloatField(default=0)),
                ('calcweight_easy', models.FloatField(default=0)),
                ('calclevel_normal', models.FloatField(default=0)),
                ('calcweight_normal', models.FloatField(default=0)),
                ('calclevel_hd', models.FloatField(default=0)),
                ('calcweight_hd', models.FloatField(default=0)),
                ('calclevel_exh', models.FloatField(default=0)),
                ('calcweight_exh', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SongComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('text', models.CharField(max_length=1000)),
                ('score', models.IntegerField(default=0)),
                ('writer', models.CharField(max_length=100)),
                ('ip', models.CharField(max_length=100)),
                ('attr', models.IntegerField(default=0)),
                ('password', models.CharField(max_length=100)),
                ('ranktable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.RankTable')),
                ('song', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='iidxrank.Song')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='song',
            unique_together=set([('songid', 'songtype')]),
        ),
        migrations.AddField(
            model_name='rankitem',
            name='song',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='iidxrank.Song'),
        ),
        migrations.AddField(
            model_name='rankcategory',
            name='ranktable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.RankTable'),
        ),
        migrations.AddField(
            model_name='playrecord',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iidxrank.Song'),
        ),
    ]
