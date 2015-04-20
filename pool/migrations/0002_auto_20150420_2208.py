# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poolspot',
            name='seat',
            field=models.ForeignKey(to='pool.Seat', null=True),
        ),
        migrations.AlterField(
            model_name='organizationseat',
            name='organization',
            field=models.ForeignKey(to='pool.Organization', null=True),
        ),
        migrations.AlterField(
            model_name='organizationseat',
            name='seat',
            field=models.ForeignKey(to='pool.Seat', null=True),
        ),
        migrations.AlterField(
            model_name='poolspot',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterUniqueTogether(
            name='poolspot',
            unique_together=set([('date', 'organization'), ('seat', 'date')]),
        ),
    ]
