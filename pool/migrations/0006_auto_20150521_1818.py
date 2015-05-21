# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0005_trip_foreign'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poolspot',
            options={'ordering': ['seat', 'date']},
        ),
        migrations.AddField(
            model_name='seat',
            name='priority',
            field=models.IntegerField(default=99),
        ),
    ]
