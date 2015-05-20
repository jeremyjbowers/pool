# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('organization_name', models.CharField(max_length=255, null=True)),
                ('organization_type', models.CharField(blank=True, max_length=255, null=True, choices=[(b'p', b'Print'), (b'm', b'Magazine'), (b'r', b'Radio'), (b't', b'Television'), (b'w', b'Web site'), (b'x', b"It's complicated")])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationSeatRotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('order', models.IntegerField(null=True)),
                ('organization', models.ForeignKey(to='pool.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('phone_number', models.CharField(max_length=255, null=True, blank=True)),
                ('preferred_contact', models.CharField(default=b'e', max_length=255, null=True, choices=[(b'e', b'Email'), (b't', b'Text')])),
                ('organization', models.ForeignKey(to='pool.Organization')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PoolSpot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateField()),
                ('organization', models.ForeignKey(blank=True, to='pool.Organization', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PoolSpotOffer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateField(null=True)),
                ('offer_code', models.CharField(max_length=255, blank=True)),
                ('organization', models.ForeignKey(to='pool.Organization')),
                ('pool_spot', models.OneToOneField(to='pool.PoolSpot')),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('foreign_eligible', models.BooleanField(default=False)),
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
                ('current_spot', models.IntegerField(null=True)),
                ('seat', models.ForeignKey(to='pool.Seat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('location', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='poolspot',
            name='seat',
            field=models.ForeignKey(to='pool.Seat', null=True),
        ),
        migrations.AddField(
            model_name='poolspot',
            name='trip',
            field=models.ForeignKey(blank=True, to='pool.Trip', null=True),
        ),
        migrations.AddField(
            model_name='organizationseatrotation',
            name='seat_rotation',
            field=models.ForeignKey(to='pool.SeatRotation'),
        ),
        migrations.AlterUniqueTogether(
            name='poolspotoffer',
            unique_together=set([('organization', 'date')]),
        ),
    ]
