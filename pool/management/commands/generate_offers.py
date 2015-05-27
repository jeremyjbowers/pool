from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from pool import models
from pool import utils

class Command(BaseCommand):
    help = 'Generates offers for outstanding seats.'


    def handle(self, *args, **options):
        for seat in models.Seat.objects.filter(foreign_eligible=True).order_by('priority'):
            pool_spots = models.PoolSpot.objects.filter(seat=seat, organization__isnull=True).order_by('date')

            if pool_spots.count() > 0:
                pool_spot = pool_spots[0]

                rotation = models.SeatRotation.objects.get(seat=seat)
                next_organization, idx, seat_pool = rotation.get_next_organization()
                p = models.PoolSpotOffer(pool_spot=pool_spot, organization=next_organization.organization, active=True)
                p.set_offer_code()

                try:
                    p.save()
                    p.make_offer()
                    rotation.current_spot = next_organization.order
                    rotation.save()

                except IntegrityError, e:
                    next_organization = utils.increment_seat_order(next_organization.order, seat_pool)
                    next_organization = models.OrganizationSeatRotation.objects.get(seat_rotation=rotation, order=next_organization)
                    rotation.current_spot = next_organization.order
                    rotation.save()