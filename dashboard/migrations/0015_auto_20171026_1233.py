# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-26 06:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0014_auto_20171026_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventory',
            old_name='added_by',
            new_name='created_by',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='notifier',
            new_name='created_by',
        ),
        migrations.RenameField(
            model_name='requisition',
            old_name='ordered_by',
            new_name='created_by',
        ),
        migrations.AddField(
            model_name='material',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submaterial',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transactionhistory',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
