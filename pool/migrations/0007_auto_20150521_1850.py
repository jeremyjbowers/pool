# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0006_auto_20150521_1818'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poolspot',
            options={'ordering': ['seat__priority', 'date']},
        ),
    ]
