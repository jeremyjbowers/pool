from django.contrib import admin

from pool import models

admin.site.register(models.Seat)
admin.site.register(models.Organization)
admin.site.register(models.OrganizationSeat)
admin.site.register(models.PoolSpot)
admin.site.register(models.PoolSpotOffer)