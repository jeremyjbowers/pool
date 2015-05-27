# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0007_auto_20150521_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='poolspotoffer',
            name='resolving_user',
            field=models.ForeignKey(blank=True, to='pool.OrganizationUser', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='poolspotoffer',
            unique_together=set([('organization', 'date', 'active')]),
        ),
    ]
