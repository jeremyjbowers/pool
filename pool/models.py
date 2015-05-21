import json
import os
import uuid

from dateutil.rrule import *
from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
from django.conf import settings
import requests
from twilio.rest import TwilioRestClient

from pool import utils

ORGANIZATION_CONTACT_CHOICES = (
    ('e', 'Email'),
    ('t', 'Text'),
)

ORGANIZATION_TYPE_CHOICES = (
    ('p', 'Print'),
    ('m', 'Magazine'),
    ('r', 'Radio'),
    ('t', 'Television'),
    ('w', 'Web site'),
    ('x', 'It\'s complicated'),
)


class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super(ActiveUserManager, self).get_queryset().filter(active=True, verified=True)


class ActiveObjectsManager(models.Manager):
    def get_queryset(self):
        return super(ActiveObjectsManager, self).get_queryset().filter(active=True)


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveObjectsManager()

    class Meta:
        abstract = True

    def dict(self):
        return dict(json.loads(serializers.serialize('json', [self]))[0]['fields'])

    def json(self):
        return json.dumps(self.dict())


class Trip(TimeStampedMixin):
    location = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return "%s: %s to %s" % (self.location, self.start_date, self.end_date)

    def assign_pool_spots(self):
        spot_dates = list(rrule(DAILY, dtstart=self.start_date, until=self.end_date))
        for date in spot_dates:
            for seat in Seat.objects.all().filter(foreign_eligible=True):
                obj, created = PoolSpot.objects.update_or_create(seat=seat, date=date)

    def save(self, *args, **kwargs):
        self.assign_pool_spots()
        super(Trip, self).save(*args, **kwargs)


class Seat(TimeStampedMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    foreign_eligible = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s seat" % self.name


class Organization(TimeStampedMixin):
    organization_name = models.CharField(max_length=255, null=True)
    organization_type = models.CharField(choices=ORGANIZATION_TYPE_CHOICES, max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.organization_name

    def send_message(self, message):
        if self.preferred_contact == 'e':
            utils.send_email(self, message)

        if self.preferred_contact == 't':
            utils.send_text(self, message)


class OrganizationUser(TimeStampedMixin):
    organization = models.ForeignKey(Organization)
    user = models.OneToOneField(User)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    dirty_phone = models.BooleanField(default=False)
    preferred_contact = models.CharField(choices=ORGANIZATION_CONTACT_CHOICES, max_length=255, default="e", null=True)
    temporary_code = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(default=False)

    active_users = ActiveUserManager()

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        return self.user.get_full_name()

    def set_temporary_code(self):
        if not self.temporary_code:
            self.temporary_code = str(uuid.uuid4())

    def save(self, *args, **kwargs):

        # handle dirty phone numbers by defaulting to email
        if self.dirty_phone and self.preferred_contact == "t":
            self.preferred_contact = "e"

        # if you are unverified, assign a temporary code we
        # can use to verify you.
        if not self.verified and not self.temporary_code:
            self.set_temporary_code()

        super(OrganizationUser, self).save(*args, **kwargs)

class PoolSpot(TimeStampedMixin):
    seat = models.ForeignKey(Seat, null=True)
    date = models.DateField()
    organization = models.ForeignKey(Organization, blank=True, null=True)
    trip = models.ForeignKey(Trip, blank=True, null=True)

    def __unicode__(self):
        if self.organization:
            return "%s on %s: CLAIMED by %s" % (self.seat, self.date, self.organization)
        return "%s on %s" % (self.seat, self.date)

    def remove_accepted_pool_spot(self):
        return PoolSpotOffer.objects.get(organization=self.organization, pool_spot=self).delete()

    def save(self, *args, **kwargs):
        if self.organization:
            self.remove_accepted_pool_spot()
        super(PoolSpot, self).save(*args, **kwargs)


class PoolSpotOffer(TimeStampedMixin):
    pool_spot = models.OneToOneField(PoolSpot)
    date = models.DateField(null=True)
    organization = models.ForeignKey(Organization)
    offer_code = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [('organization', 'date')]

    def __unicode__(self):
        return "%s offered to %s" % (self.pool_spot, self.organization)

    def save(self, *args, **kwargs):
        self.set_offer_code()
        if not self.date:
            self.date = self.pool_spot.date
        super(PoolSpotOffer, self).save(*args, **kwargs)

    def set_offer_code(self):
        if not self.offer_code:
            self.offer_code = str(uuid.uuid4())

    def get_accept_url(self):
        return '%s/pool/offer/seat/accept/%s/' % (settings.HOST_NAME, self.offer_code)

    def get_decline_url(self):
        return '%s/pool/offer/seat/decline/%s/' % (settings.HOST_NAME, self.offer_code)

    def make_offer(self):
        message = {}
        message['subject'] = 'Action required: %s pool spot on %s' % (self.pool_spot.seat, self.pool_spot.date)
        message['body'] = 'The %s on %s is available.\n\nAccept: %s\n\nDecline: %s' % (
            self.pool_spot.seat,
            self.pool_spot.date,
            self.get_accept_url(),
            self.get_decline_url()
        )
        self.organization.send_message(message)


class SeatRotation(TimeStampedMixin):
    seat = models.ForeignKey(Seat)
    current_spot = models.IntegerField(null=True)

    def __unicode__(self):
        return "Rotation for %s" % self.seat

    def get_next_organization(self):
        """
        Decides which organization should get the next offfer.
        tk Logic for making sure the same company does not get offers
        for more than one seat (?).
        """
        seat_pool = sorted([s.order for s in OrganizationSeatRotation.objects.filter(seat_rotation=self).order_by('order')])
        for idx, seat_order in enumerate(seat_pool):
            if seat_order == self.current_spot:
                next_organization = utils.increment_seat_order(idx, seat_pool)
                next_organization = OrganizationSeatRotation.objects.get(seat_rotation=self, order=next_organization)
                return next_organization, idx, seat_pool


class OrganizationSeatRotation(TimeStampedMixin):
    seat_rotation = models.ForeignKey(SeatRotation)
    organization = models.ForeignKey(Organization)
    order = models.IntegerField(null=True)

    def __unicode__(self):
        return "%s in %s rotation" % (self.organization, self.seat_rotation)