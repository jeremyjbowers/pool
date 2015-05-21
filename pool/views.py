import json

from django.views.generic import ListView, DetailView
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.template.context_processors import csrf

from pool import models
from pool import utils

def create_user(request):
    if request.method == "POST":
        REQUIRED_PARAMS = ['first_name', 'last_name', 'email_address', 'username', 'phone_number', 'preferred_contact', 'organization_id']
        valid = True

        for param in REQUIRED_PARAMS:
            if not request.POST.get(param, None):
                valid = False

        if valid:
            organization = models.Organization.objects.get(id=request.POST['organization_id'])
            context = {}
            context['organization'] = organization

            try:
                user = User.objects.create_user(request.POST['username'], request.POST['email_address'], request.POST['password'])
                user.first_name = request.POST['first_name']
                user.last_name = request.POST['last_name']
                user.save()
                context['user'] = user

            except IntegrityError:
                context['error'] = "Whoops, your user account already exists.<br/>Should we get you a new password?"
                return render_to_response('pool/create_user_fail.html', context)

            try:
                phone, dirty = utils.format_phone_number(request.POST['phone_number'])
                organization_user = models.OrganizationUser(user=user,
                                                        organization=organization,
                                                        phone_number=phone,
                                                        dirty_phone=dirty,
                                                        preferred_contact=request.POST['preferred_contact'])
                organization_user.save()
                context['organization_user'] = organization_user

            except IntegrityError:
                context['error'] = "Whoops, your user account already exists.<br/>Should we get you a new password?"
                return render_to_response('pool/create_user_fail.html', context)

            return render_to_response('pool/create_user_success.html', context)

        else:
            return HttpResponse('400 error')

    if request.method == "GET":
        context = {}
        context.update(csrf(request))
        context['organizations'] = models.Organization.objects.all().values('organization_name', 'id').order_by('organization_name')
        return render_to_response('pool/create_user.html', context)

def resolve_seat_offer(request, offer_action, offer_code):
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
            offer.delete()
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