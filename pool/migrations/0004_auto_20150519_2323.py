# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0003_auto_20150420_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='seat',
            name='foreign_eligible',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='organizationseat',
            unique_together=set([('seat', 'order'), ('seat', 'organization')]),
        ),
        migrations.AddField(
            model_name='poolspot',
            name='trip',
            field=models.ForeignKey(blank=True, to='pool.Trip', null=True),
        ),
    ]
