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

def verify_user(request, temporary_code):
    context = {}
    context['host_name'] = settings.HOST_NAME

    try:
        u = models.OrganizationUser.objects.get(temporary_code=temporary_code)
        u.verified = True
        u.temporary_code = None
        u.save()
        context['user'] = u
        return render_to_response('pool/verify_user_success.html', context)
    except models.OrganizationUser.DoesNotExist:
        context['error'] = "Whoops, we can't find a user that matches this key.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help."
        return render_to_response('pool/verify_user_fail.html', context)


def create_user(request):
    context = {}
    context['host_name'] = settings.HOST_NAME

    if request.method == "POST":

        # must have these params.
        REQUIRED_PARAMS = ['first_name', 'last_name', 'email_address', 'username', 'phone_number', 'preferred_contact', 'organization_id', 'password']
        for param in REQUIRED_PARAMS:
            if not request.POST.get(param, None):
                context['error'] = "Whoops, you're missing a parameter, <strong>%s</strong>, in your request.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help." % param
                return render_to_response('pool/create_user_fail.html', context)

        # clean the raw text fields
        first_name = utils.clean_unicode(request.POST['first_name'])
        last_name = utils.clean_unicode(request.POST['last_name'])
        phone_number, dirty = utils.format_phone_number(request.POST['phone_number'])
        email_address = utils.clean_unicode(request.POST['email_address'])
        username = utils.clean_unicode(request.POST['username'])
        password = utils.clean_unicode(request.POST['password'])

        # check username duplication
        if User.objects.filter(username=username).count() > 0:
            context['error'] = "Whoops, the username <strong>%s</strong> already exists.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help." % username
            return render_to_response('pool/create_user_fail.html', context)

        # check email duplication
        if User.objects.filter(email=email_address).count() > 0:
            context['error'] = "Whoops, someone with the email address <strong>%s</strong> already exists.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help." % email_address
            return render_to_response('pool/create_user_fail.html', context)

        # check phone duplication
        if models.OrganizationUser.objects.filter(phone_number=phone_number).count() > 0:
            context['error'] = "Whoops, someone with the phone number <strong>%s</strong> already exists.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help." % phone_number
            return render_to_response('pool/create_user_fail.html', context)

        # lookup the organization
        organization = models.Organization.objects.get(id=request.POST['organization_id'])
        context['organization'] = organization

        # try to create the user account first
        try:
            user = User.objects.create_user(username, email_address, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            context['user'] = user

        except IntegrityError:

            # this should be the "already exists" flow
            context['error'] = "Whoops, your user account already exists.<br/>Should we get you a new password?"
            return render_to_response('pool/create_user_fail.html', context)

        # then try and create the organization_user
        try:
            organization_user = models.OrganizationUser(user=user,
                                                    organization=organization,
                                                    phone_number=phone_number,
                                                    dirty_phone=dirty,
                                                    preferred_contact=request.POST['preferred_contact'])
            organization_user.save()
            context['organization_user'] = organization_user

        except IntegrityError:

            # this should be the "already exists" flow
            context['error'] = "Whoops, your user account already exists.<br/>Should we get you a new password?"
            return render_to_response('pool/create_user_fail.html', context)

        # it worked so return something nice.
        # should probably send the "are you real" email
        message = {}
        message['subject'] = "whitehousepool.org: Verify your email"
        message['body'] = "Someone registered an account with http://whitehousepool.org/ from this account<br/>"
        message['body'] += "If this was you, please click this link to verify your account.<br/>"
        message['body'] += "<a href='%s/pool/user/verify/%s/'>verify my account</a>" % (settings.HOST_NAME, organization_user.temporary_code)
        utils.send_email(organization_user, message)
        return render_to_response('pool/create_user_success.html', context)

    if request.method == "GET":
        context.update(csrf(request))
        context['organizations'] = models.Organization.objects.all().values('organization_name', 'id').order_by('organization_name')
        return render_to_response('pool/create_user.html', context)

def resolve_seat_offer(request, offer_action, offer_code):
    context = {}
    context['host_name'] = settings.HOST_NAME

    try:
        offer = models.PoolSpotOffer.objects.get(offer_code=offer_code)
        if offer_action == "accept":
            offer.pool_spot.organization = offer.organization
            offer.pool_spot.save()
            message = '%s<br/>You have accepted the pool spot for the %s seat on %s.' % (
                offer.organization.organization_name,
                offer.pool_spot.seat.name,
                offer.pool_spot.date
            )
        if offer_action == "decline":
            offer.delete()
            message = '%s<br/>You have declined the pool spot for the %s seat on %s.' % (
                offer.organization.organization_name,
                offer.pool_spot.seat.name,
                offer.pool_spot.date
            )

        return HttpResponse(message)

    except models.PoolSpotOffer.DoesNotExist:
        return HttpResponse("A seat matching your query does not exist.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help.")