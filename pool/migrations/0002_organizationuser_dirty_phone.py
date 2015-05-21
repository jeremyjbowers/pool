# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationuser',
            name='dirty_phone',
            field=models.BooleanField(default=False),
        ),
    ]
