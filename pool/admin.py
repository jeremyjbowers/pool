from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from pool import models

class OrganizationSeatRotationInline(admin.TabularInline):
    model = models.OrganizationSeatRotation
    extra = 0


class OrganizationUserInline(admin.TabularInline):
    model = models.OrganizationUser
    extra = 0


class SeatRotationAdmin(admin.ModelAdmin):
    inlines = [OrganizationSeatRotationInline]


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationUserInline]


class UserAdmin(UserAdmin):
    inlines = [OrganizationUserInline]


class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'get_email', 'phone_number', 'active']
    list_editable = ['active']

admin.site.register(models.SeatRotation, SeatRotationAdmin)
admin.site.register(models.Seat)
admin.site.register(models.Trip)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.PoolSpot)
admin.site.register(models.PoolSpotOffer)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(models.OrganizationUser, OrganizationUserAdmin)