# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-01 21:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0002_auto_20180502_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectorcampaign',
            name='copy_connector_id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='connectorcampaign',
            name='created_by_id',
            field=models.IntegerField(),
        ),
    ]
