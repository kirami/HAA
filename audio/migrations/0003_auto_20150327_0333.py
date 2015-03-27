# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0002_auto_20150327_0332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='notes',
            field=models.CharField(default='', max_length=800, null=True, blank=True),
            preserve_default=True,
        ),
    ]
