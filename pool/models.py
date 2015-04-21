import json
import os
import uuid

from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
import requests
from twilio.rest import TwilioRestClient

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


class Seat(TimeStampedMixin):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s seat" % self.name


class Organization(TimeStampedMixin):
    organization_name = models.CharField(max_length=255)
    organization_type = models.CharField(choices=ORGANIZATION_TYPE_CHOICES, max_length=255, null=True, blank=True)
    user = models.OneToOneField(User)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    preferred_contact = models.CharField(choices=ORGANIZATION_CONTACT_CHOICES, max_length=255, default="e")

    def __unicode__(self):
        return self.organization_name

    def send_text(self, message):
        client = TwilioRestClient(
            os.environ.get('POOL_TWILIO_ACCOUNT_SID', None),
            os.environ.get('POOL_TWILIO_AUTH_TOKEN', None)
        )
        b = client.messages.create(
            body=message.get('body', None),
            to="+1%s" % self.phone_number,
            from_=os.environ.get('POOL_TWILIO_PHONE_NUMBER', None),
        )

    def send_email(self, message):
        return requests.post(
            "https://api.mailgun.net/v3/mg.whitehousepool.org/messages",
            auth=("api", os.environ.get('POOL_MAILGUN_API_KEY', None)),
            data={"from": "PoolBot <mailgun@mg.whitehousepool.org>",
                "to": [self.user.email],
                "subject": message.get('subject', None),
                "text": message.get('body', None)
            }
        )

    def send_message(self, message):
        if self.preferred_contact == 'e':
            self.send_email(message)

        if self.preferred_contact == 't':
            self.send_text(message)


class OrganizationSeat(TimeStampedMixin):
    seat = models.ForeignKey(Seat, null=True)
    organization = models.ForeignKey(Organization, null=True)
    order = models.IntegerField()

    class Meta:
        unique_together = (('seat', 'order'), ('seat', 'organization'))

    def __unicode__(self):
        return "%s seat: %s (%s)" % (self.seat, self.organization, self.order)

    def get_next_organization(self):
        seat_pool = sorted([s.order for s in OrganizationSeat.objects.filter(seat=self.seat)])
        for idx, seat_order in enumerate(seat_pool):
            if seat_order == self.order:
                print idx, idx+1, len(seat_pool), seat_pool
                try:
                    next_organization = seat_pool[idx+1]
                except IndexError:
                    next_organization = seat_pool[0]
                return OrganizationSeat.objects.get(seat=self.seat, order=next_organization)



class PoolSpot(TimeStampedMixin):
    seat = models.ForeignKey(Seat, null=True)
    date = models.DateField()
    organization = models.ForeignKey(Organization, blank=True, null=True)

    class Meta:
        unique_together = (('seat', 'date'), ('date', 'organization'))

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
    organization = models.ForeignKey(Organization)
    offer_code = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return "%s offered to %s" % (self.pool_spot, self.organization)

    def save(self, *args, **kwargs):
        self.set_offer_code()
        super(PoolSpotOffer, self).save(*args, **kwargs)

    def set_offer_code(self):
        if not self.offer_code:
            self.offer_code = str(uuid.uuid4())

    def get_accept_url(self):
        return 'http://127.0.0.1:8000/pool/offer/accept/%s/' % self.offer_code

    def get_decline_url(self):
        return 'http://127.0.0.1:8000/pool/offer/decline/%s/' % self.offer_code

    def make_offer(self):
        message = {}
        message['subject'] = None
        message['body'] = 'The %s on %s is available.\n\nAccept: %s\n\nDecline: %s' % (
            self.pool_spot.seat,
            self.pool_spot.date,
            self.get_accept_url(),
            self.get_decline_url()
        )
        self.organization.send_message(message)

    def generate_next_offer(self):
        o = OrganizationSeat.objects.get(seat=self.pool_spot.seat, organization=self.organization)
        next_organization = o.get_next_organization()
        p = PoolSpotOffer(pool_spot=self.pool_spot, organization=next_organization.organization)
        p.set_offer_code()
        self.delete()
        p.save()
        p.make_offer()