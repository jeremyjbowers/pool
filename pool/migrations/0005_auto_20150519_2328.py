# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0004_auto_20150519_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='location',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
