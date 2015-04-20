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
                ('organization_name', models.CharField(max_length=255)),
                ('organization_type', models.CharField(blank=True, max_length=255, null=True, choices=[(b'p', b'Print'), (b'm', b'Magazine'), (b'r', b'Radio'), (b't', b'Television'), (b'w', b'Web site'), (b'x', b"It's complicated")])),
                ('phone_number', models.CharField(max_length=255, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationSeat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('order', models.IntegerField()),
                ('organization', models.ForeignKey(to='pool.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='PoolSpot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateField(unique=True)),
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
                ('offer_code', models.CharField(max_length=255)),
                ('organization', models.ForeignKey(to='pool.Organization')),
                ('pool_spot', models.OneToOneField(to='pool.PoolSpot')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='organizationseat',
            name='seat',
            field=models.ForeignKey(to='pool.Seat'),
        ),
        migrations.AlterUniqueTogether(
            name='organizationseat',
            unique_together=set([('seat', 'organization', 'order')]),
        ),
    ]
