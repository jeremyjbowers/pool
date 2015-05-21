# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0002_organizationuser_dirty_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationuser',
            name='temporary_code',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='organizationuser',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
