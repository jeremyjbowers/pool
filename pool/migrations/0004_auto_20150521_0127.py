# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0003_auto_20150521_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationuser',
            name='temporary_code',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
