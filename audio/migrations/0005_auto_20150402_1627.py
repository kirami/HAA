# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0004_auto_20150331_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
