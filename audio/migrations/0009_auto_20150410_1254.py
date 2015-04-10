# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0008_auto_20150410_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='description',
            field=models.TextField(null=True, blank=True, default=''),
            preserve_default=True,
        ),
    ]
