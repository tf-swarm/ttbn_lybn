# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-12-04 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RedGetData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('red_packet_id', models.CharField(default='1547623377', max_length=60)),
                ('uid', models.BigIntegerField()),
                ('nick', models.CharField(max_length=100)),
                ('packet', models.BigIntegerField()),
                ('time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='RedPacketInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('special_id', models.CharField(default='1547623377', max_length=60)),
                ('stop_state', models.IntegerField()),
                ('special_end_time', models.BigIntegerField()),
                ('red_packet_type', models.BigIntegerField()),
                ('day_time', models.DateTimeField()),
                ('insert_time', models.DateTimeField()),
                ('day_stamp', models.BigIntegerField()),
                ('json_data', models.CharField(max_length=16000)),
            ],
        ),
    ]
