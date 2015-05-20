# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0007_auto_20150519_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='seatrotation',
            name='current_spot',
            field=models.IntegerField(null=True),
        ),
    ]
