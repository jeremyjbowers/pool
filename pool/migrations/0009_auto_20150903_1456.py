# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0008_auto_20150527_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poolspotoffer',
            name='pool_spot',
            field=models.ForeignKey(to='pool.PoolSpot'),
        ),
    ]
