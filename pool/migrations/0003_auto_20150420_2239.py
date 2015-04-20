# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0002_auto_20150420_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='preferred_contact',
            field=models.CharField(default=b'e', max_length=255, choices=[(b'e', b'Email'), (b't', b'Text')]),
        ),
        migrations.AlterField(
            model_name='poolspotoffer',
            name='offer_code',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
