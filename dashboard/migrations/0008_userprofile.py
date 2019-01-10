# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-25 05:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0007_transactionhistory_invoice_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_finance', models.BooleanField(default=False)),
                ('is_inventory', models.BooleanField(default=False)),
                ('is_officer', models.BooleanField(default=False)),
                ('avatar', models.CharField(max_length=150)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]