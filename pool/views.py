from django.views.generic import ListView, DetailView
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Sum, Count

from pool import models

def offer_action(request, offer_action, offer_code):
    try:
        offer = models.PoolSpotOffer.objects.get(offer_code=offer_code)
        if offer_action == "accept":
            offer.pool_spot.organization = offer.organization
            offer.pool_spot.save()
            message = '<h2>%s %s, %s</h2><p>You have accepted the pool spot for the %s seat on %s.</p><p>Thank you.</p>' % (
                offer.organization.user.first_name,
                offer.organization.user.last_name,
                offer.organization.organization_name,
                offer.pool_spot.seat.name,
                offer.pool_spot.date
            )
        if offer_action == "decline":
            offer.generate_next_offer()
            message = '<h2>%s %s, %s</h2><p>You have declined the pool spot for the %s seat on %s.</p><p>Thank you.</p>' % (
                offer.organization.user.first_name,
                offer.organization.user.last_name,
                offer.organization.organization_name,
                offer.pool_spot.seat.name,
                offer.pool_spot.date
            )

        return HttpResponse(message)

    except models.PoolSpotOffer.DoesNotExist:
        return HttpResponse('<p>A seat matching your query does not exist.</p><p>Thank you.</p>')