# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0007_auction_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='description',
            field=models.TextField(max_length=600, blank=True, null=True, default=''),
            preserve_default=True,
        ),
    ]
