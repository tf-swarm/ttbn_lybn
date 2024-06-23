# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-12-02 16:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_data', models.CharField(default='', max_length=2600)),
            ],
        ),
        migrations.CreateModel(
            name='LoginInfo',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('account_name', models.CharField(default='', max_length=50)),
                ('limit_level', models.IntegerField(default=0)),
                ('login_limit', models.IntegerField()),
                ('limit', models.IntegerField(default=1)),
                ('phone', models.CharField(default='', max_length=50)),
                ('department', models.CharField(default='', max_length=100)),
                ('ip_address', models.CharField(default='', max_length=50)),
                ('url', models.CharField(default='', max_length=50)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('login_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='ProductList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(default='', max_length=16)),
                ('product_data', models.CharField(default='', max_length=900)),
            ],
        ),
        migrations.CreateModel(
            name='VerifyCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=50)),
                ('verify', models.CharField(max_length=6)),
                ('times', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
