# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0006_item_notes_two'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='description',
            field=models.CharField(default='', max_length=600, blank=True, null=True),
            preserve_default=True,
        ),
    ]
