# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-20 05:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_bill', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('received_bill', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bill',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_no', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'client',
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roll_id', models.CharField(default='', max_length=50)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available_weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('type', models.CharField(default='local', max_length=10)),
                ('status', models.CharField(default='stock', max_length=10)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'stock',
            },
        ),
        migrations.CreateModel(
            name='InventoryExchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.IntegerField(default=0)),
                ('exchange_type', models.CharField(db_index=True, default='in', max_length=10)),
                ('exchange_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'inventory_exchange',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Untitled Material', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'material',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_order', models.CharField(default='Unknown PO', max_length=100)),
                ('name', models.CharField(default='Untitled Order', max_length=100)),
                ('layer', models.SmallIntegerField(default=1)),
                ('amount', models.IntegerField(default=0)),
                ('production_amount', models.IntegerField(default=0)),
                ('bill_per_production', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_bill', models.FloatField(default=0)),
                ('is_in_production', models.BooleanField(default=False)),
                ('is_produced', models.BooleanField(default=False)),
                ('is_shipped', models.BooleanField(default=False)),
                ('is_paid', models.BooleanField(default=False)),
                ('delivery_date', models.DateField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='dashboard.Client')),
            ],
            options={
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='OrderQuantity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('required_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('checkout_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Material')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Order')),
                ('stock', models.ManyToManyField(to='dashboard.Inventory')),
            ],
            options={
                'db_table': 'order_quantity',
            },
        ),
        migrations.CreateModel(
            name='ProductionExchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('exchange_type', models.CharField(db_index=True, default='in', max_length=10)),
                ('exchange_date', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Order')),
            ],
            options={
                'db_table': 'production_exchange',
            },
        ),
        migrations.CreateModel(
            name='Requisition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_arrived', models.BooleanField(default=False)),
                ('received_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created', models.DateTimeField(auto_now=True)),
                ('ordered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'requisition',
            },
        ),
        migrations.CreateModel(
            name='SubMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='', max_length=10)),
                ('name', models.CharField(default='Untitled Material', max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Material')),
            ],
            options={
                'db_table': 'sub_material',
            },
        ),
        migrations.CreateModel(
            name='TransactionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('exchange_date', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Client')),
            ],
            options={
                'db_table': 'transaction_history',
            },
        ),
        migrations.AddField(
            model_name='requisition',
            name='sub_material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.SubMaterial'),
        ),
        migrations.AddField(
            model_name='orderquantity',
            name='sub_material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.SubMaterial'),
        ),
        migrations.AddField(
            model_name='order',
            name='structure',
            field=models.ManyToManyField(through='dashboard.OrderQuantity', to='dashboard.Material'),
        ),
        migrations.AddField(
            model_name='inventoryexchange',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.Order'),
        ),
        migrations.AddField(
            model_name='inventoryexchange',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Inventory'),
        ),
        migrations.AddField(
            model_name='inventory',
            name='requisition',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inventory', to='dashboard.Requisition'),
        ),
        migrations.AddField(
            model_name='inventory',
            name='sub_material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='dashboard.SubMaterial'),
        ),
        migrations.AddField(
            model_name='bill',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.Client'),
        ),
    ]
