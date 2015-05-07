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
            name='label',
            field=models.ForeignKey(null=True, blank=True, to='audio.Label', related_name='itemLabel'),
            preserve_default=True,
        ),
    ]
