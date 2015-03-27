# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='artist',
            field=models.CharField(blank=True, max_length=400, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='artist_two',
            field=models.CharField(blank=True, max_length=400, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(default='', max_length=400),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='name_two',
            field=models.CharField(blank=True, max_length=400, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='notes',
            field=models.CharField(blank=True, max_length=400, default='', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='prefix',
            field=models.CharField(blank=True, max_length=600, null=True),
            preserve_default=True,
        ),
    ]
