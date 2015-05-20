from django.contrib import admin

from pool import models

class OrganizationSeatRotationInline(admin.TabularInline):
    model = models.OrganizationSeatRotation
    extra = 0

class SeatRotationAdmin(admin.ModelAdmin):
    inlines = [OrganizationSeatRotationInline]

admin.site.register(models.SeatRotation, SeatRotationAdmin)
admin.site.register(models.Seat)
admin.site.register(models.Trip)
admin.site.register(models.Organization)
# admin.site.register(models.OrganizationSeat)
admin.site.register(models.PoolSpot)
admin.site.register(models.PoolSpotOffer)