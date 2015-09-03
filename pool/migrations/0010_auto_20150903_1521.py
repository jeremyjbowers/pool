# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0009_auto_20150903_1456'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seat',
            old_name='foreign_eligible',
            new_name='foreign',
        ),
    ]
