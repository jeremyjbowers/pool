# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0006_auto_20150519_2335'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='organizationseat',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='organizationseat',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='organizationseat',
            name='seat',
        ),
        migrations.AddField(
            model_name='organizationseatrotation',
            name='order',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='OrganizationSeat',
        ),
    ]
