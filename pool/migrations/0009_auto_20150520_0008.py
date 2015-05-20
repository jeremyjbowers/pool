# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0008_seatrotation_current_spot'),
    ]

    operations = [
        migrations.AddField(
            model_name='poolspotoffer',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='poolspotoffer',
            unique_together=set([('organization', 'date')]),
        ),
    ]
