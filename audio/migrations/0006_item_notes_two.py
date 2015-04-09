# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0005_auto_20150402_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='notes_two',
            field=models.CharField(max_length=800, default='', null=True, blank=True),
            preserve_default=True,
        ),
    ]
