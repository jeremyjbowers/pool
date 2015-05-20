# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0005_auto_20150519_2328'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationSeatRotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(to='pool.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SeatRotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('seat', models.ForeignKey(to='pool.Seat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='organizationseatrotation',
            name='seat_rotation',
            field=models.ForeignKey(to='pool.SeatRotation'),
        ),
    ]
