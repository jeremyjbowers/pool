from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from pool import models
from pool import utils

class Command(BaseCommand):
    help = 'Generates offers for outstanding seats.'


    def handle(self, *args, **options):

        # Build a list of all active trips. We'll deal with them in order of their start_date.
        trips = models.Trip.objects.filter(active=True).order_by('start_date')

        # As long as we have at least one active trip, go through the process.
        if len(trips) > 0:

            # Grab the first trip from the list.
            # We only assign seats to one trip at a time.
            trip = trips[0]

            # Build a list of pool spots associated with this trip.
            # Sort the list by seat priority and date.
            # E.g., finish assigning each seat in order of priority before
            # starting on the next seat.
            # There are overlapping pools, and the higher priority seat
            # might determine who is eligible for the next seat.
            pool_spots = models.PoolSpot.objects.filter(organization__isnull=True, active=True, trip=trip).order_by('-seat__priority', 'date')

            # Grab the first seat from the list.
            # We only assign on e spot at a time.
            pool_spot = pool_spots[0]
            seat = pool_spot.seat

            # If we're waiting on a response, give up and wait.
            if pool_spot.has_outstanding_offer():
                print "Waiting on response from %s to %s." % (pool_spot.offer().organization, seat)

            else:

                # If we can assign a new offer, go through the process.
                # First, find the rotation we're talking about.
                rotation = models.SeatRotation.objects.get(seat=seat)

                # Figure out who is next.
                next_organization, idx, seat_pool = rotation.get_next_organization()

                # Make an offer to the next organization.
                try:
                    p = models.PoolSpotOffer(pool_spot=pool_spot, organization=next_organization.organization)
                    p.set_offer_code()
                    p.active = True
                    p.save()
                    p.make_offer()

                except IntegrityError:
                    # Skip to the next if we can't insert because we prevent insertion if
                    # this organization is already in a seat today.
                    next_organization, idx, seat_pool = rotation.get_next_organization()

                # Update where we are in the rotation.
                rotation.current_spot = next_organization.order
                rotation.save()
                print "Offering %s seat to %s" % (seat, next_organization)