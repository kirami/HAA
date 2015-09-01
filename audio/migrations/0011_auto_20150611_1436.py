# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0010_auto_20150511_1228'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='label',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, null=True, default=''),
            preserve_default=True,
        ),
    ]
