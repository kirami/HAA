# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0009_auto_20150410_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='auction',
            field=models.ForeignKey(to='audio.Auction', related_name='itemAuction'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.ForeignKey(to='audio.Label', related_name='itemLabel', blank=True, null=True),
            preserve_default=True,
        ),
    ]
