# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-26 10:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_auto_20171026_1334'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='created',
            new_name='created_at',
        ),
    ]
