# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-21 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_remove_orderquantity_checkout_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionhistory',
            name='invoice_number',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
