# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('address_one', models.CharField(max_length=100, default='')),
                ('address_two', models.CharField(max_length=100, blank=True, null=True)),
                ('address_three', models.CharField(max_length=100, blank=True, null=True)),
                ('city', models.CharField(max_length=100, blank=True, null=True)),
                ('state', models.CharField(max_length=100, blank=True, null=True)),
                ('zipcode', models.CharField(max_length=100, blank=True, null=True, default='')),
                ('postal_code', models.CharField(max_length=100, blank=True, null=True)),
                ('country', models.CharField(max_length=100, default='')),
                ('telephone', models.CharField(max_length=100, default='')),
                ('fax', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('second_chance_start_date', models.DateTimeField(null=True)),
                ('second_chance_end_date', models.DateTimeField(null=True)),
                ('blind_locked', models.BooleanField(default=False)),
                ('flat_locked', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200, blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2, default=2.0)),
                ('winner', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=250)),
                ('min_bid', models.DecimalField(max_digits=19, blank=True, decimal_places=2, null=True)),
                ('order_number', models.IntegerField(default=None)),
                ('auction', models.ForeignKey(to='audio.Auction')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('message', models.CharField(max_length=250, default='')),
                ('done', models.BooleanField(default=False)),
                ('auction', models.ForeignKey(to='audio.Auction')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Consignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('percentage', models.DecimalField(max_digits=19, decimal_places=2)),
                ('minimum', models.DecimalField(max_digits=19, decimal_places=2)),
                ('maximum', models.DecimalField(max_digits=19, blank=True, decimal_places=2, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Consignor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('address', models.ForeignKey(blank=True, null=True, to='audio.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('invoiced_amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('invoice_date', models.DateField()),
                ('reminder_invoice_date', models.DateField(blank=True, null=True)),
                ('second_chance_invoice_amount', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('second_chance_invoice_date', models.DateField(blank=True, null=True)),
                ('shipped_date', models.DateField(blank=True, null=True)),
                ('on_hold', models.BooleanField(default=False)),
                ('shipping', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('second_chance_shipping', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('tax', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('second_chance_tax', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('discount', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('discount_percent', models.DecimalField(max_digits=19, decimal_places=2, default=0)),
                ('auction', models.ForeignKey(to='audio.Auction')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='userInvoice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('artist', models.CharField(max_length=200, blank=True, null=True)),
                ('artist_two', models.CharField(max_length=200, blank=True, null=True)),
                ('name', models.CharField(max_length=200, default='')),
                ('name_two', models.CharField(max_length=200, blank=True, null=True)),
                ('notes', models.CharField(max_length=200, blank=True, null=True, default='')),
                ('record_number', models.CharField(max_length=100, blank=True, null=True)),
                ('record_number_two', models.CharField(max_length=100, blank=True, null=True)),
                ('min_bid', models.DecimalField(max_digits=19, decimal_places=2)),
                ('lot_id', models.IntegerField(blank=True, null=True)),
                ('condition', models.CharField(max_length=100, default='')),
                ('defect', models.CharField(max_length=100, blank=True, null=True, default='')),
                ('quantity', models.IntegerField(default=1)),
                ('thumbnail', models.FileField(blank=True, null=True, upload_to='items/')),
                ('image', models.FileField(blank=True, null=True, upload_to='items/')),
                ('prefix', models.CharField(max_length=200, blank=True, null=True)),
                ('auction', models.ForeignKey(to='audio.Auction')),
                ('category', models.ForeignKey(to='audio.Category', related_name='itemCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200, default='')),
                ('notes', models.CharField(max_length=200, blank=True, null=True, default='')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(max_length=100)),
                ('parent', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('payment_type', models.CharField(max_length=100)),
                ('date_received', models.DateField()),
                ('invoice', models.ForeignKey(to='audio.Invoice', related_name='paymentInvoice')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='paymentUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrintedCatalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('auction', models.IntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='pcUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('pdf_list', models.BooleanField(default=False)),
                ('courtesy_list', models.BooleanField(default=False)),
                ('deadbeat', models.BooleanField(default=False)),
                ('email_only', models.BooleanField(default=True)),
                ('quiet', models.BooleanField(default=False)),
                ('ebay', models.BooleanField(default=False)),
                ('notes', models.CharField(max_length=200, blank=True, null=True)),
                ('verified', models.BooleanField(default=False)),
                ('confirmation_code', models.CharField(max_length=200, blank=True, null=True)),
                ('billing_address', models.ForeignKey(blank=True, related_name='upBilling', null=True, on_delete=django.db.models.deletion.SET_NULL, to='audio.Address')),
                ('shipping_address', models.ForeignKey(blank=True, related_name='upShipping', null=True, on_delete=django.db.models.deletion.SET_NULL, to='audio.Address')),
                ('user', models.ForeignKey(unique=True, related_name='upUser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='item_type',
            field=models.ForeignKey(to='audio.ItemType', related_name='itemType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='label',
            field=models.ForeignKey(blank=True, null=True, to='audio.Label'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([('auction', 'lot_id')]),
        ),
        migrations.AddField(
            model_name='consignment',
            name='consignor',
            field=models.ForeignKey(to='audio.Consignor', related_name='consignmentConsignor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='consignment',
            name='item',
            field=models.ForeignKey(to='audio.Item', related_name='consignedItem'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='consignment',
            unique_together=set([('minimum', 'item'), ('maximum', 'item')]),
        ),
        migrations.AddField(
            model_name='bid',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='audio.Invoice'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bid',
            name='item',
            field=models.ForeignKey(to='audio.Item', related_name='bidItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bid',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='bidUser'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bid',
            unique_together=set([('user', 'item')]),
        ),
    ]
