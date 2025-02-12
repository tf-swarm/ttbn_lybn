# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-12-03 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GiftInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gift_id', models.CharField(max_length=16, null=True)),
                ('gift_name', models.CharField(max_length=160, null=True)),
                ('version_id', models.CharField(max_length=16, null=True)),
                ('hot', models.CharField(max_length=6, null=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('icon_type', models.CharField(max_length=6, null=True)),
                ('price', models.BigIntegerField()),
                ('worth', models.BigIntegerField()),
                ('open_type', models.CharField(max_length=6, null=True)),
                ('limit_num', models.BigIntegerField()),
                ('vip_type', models.CharField(max_length=6, null=True)),
                ('vip_level', models.CharField(max_length=260, null=True)),
                ('detail_1', models.CharField(max_length=160, null=True)),
                ('detail_2', models.CharField(max_length=160, null=True)),
                ('detail_3', models.CharField(max_length=160, null=True)),
                ('online_state', models.IntegerField(choices=[(1, '\u4e0a\u67b6'), (2, '\u4e0b\u67b6')], default=2, null=True)),
                ('reward', models.CharField(max_length=1600, null=True)),
                ('add_time', models.IntegerField(null=True)),
                ('add_reward', models.CharField(max_length=1600, null=True)),
            ],
        ),
    ]
