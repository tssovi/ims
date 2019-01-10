# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-23 08:58
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
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('url', models.URLField(max_length=155)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'notification',
            },
        ),
        migrations.CreateModel(
            name='NotificationSeen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_seen', models.BooleanField(default=True)),
                ('seen_time', models.DateTimeField(auto_now_add=True)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Notification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notification_seen',
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='notifeed',
            field=models.ManyToManyField(through='dashboard.NotificationSeen', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='notifier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifier', to=settings.AUTH_USER_MODEL),
        ),
    ]