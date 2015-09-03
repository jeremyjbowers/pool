import datetime
import json

from django.views.generic import ListView, DetailView
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from ics import Calendar, Event

from pool import models
from pool import utils

def logout_user(request):
    logout(request)
    return redirect('/pool/login/')

@login_required
def foreign_detail(request):
    context = {}
    context['host_name'] = settings.HOST_NAME
    context['user'] = models.OrganizationUser.objects.get(user=request.user)
    context['seats'] = models.Seat.objects.filter(foreign_eligible=True, active=True).order_by('priority')
    context['trips'] = models.Trip.objects.filter(foreign=True)

    return render_to_response('pool/foreign_seat_list.html', context) 

@login_required
def pool_list(request):
    context = {}
    context['host_name'] = settings.HOST_NAME
    context['user'] = models.OrganizationUser.objects.get(user=request.user)

    return render_to_response('pool/pool_list.html', context)

def login_user(request):
    context = {}
    context['host_name'] = settings.HOST_NAME
    context['user'] = None

    if request.method == "GET":
        context.update(csrf(request))
        return render_to_response('pool/login.html', context)

    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/pool/')

    return HttpResponse('400 error')

def verify_user(request, temporary_code):
    context = {}
    context['host_name'] = settings.HOST_NAME
    context['user'] = None

    try:
        u = models.OrganizationUser.objects.get(temporary_code=temporary_code)
        u.verified = True
        u.temporary_code = None
        u.save()
        context['user'] = u
        message = {}
        message['subject'] = "whitehousepool.org: Welcome!"
        message['body'] = "Welcome to Pooler at http://whitehousepool.org/, a simple service for handling White House pool seat assignments.\n"
        message['body'] += "* You can log in here: %s/pool/login/\n" % settings.HOST_NAME
        message['body'] += "* Frequently-asked questions about Pooler: %s/pool/faq/\n" % settings.HOST_NAME
        message['body'] += "If you have questions, email jeremy.bowers@nytimes.com or michael.shear@nytimes.com.\n\n"
        message['body'] += "Thanks, and welcome!"
        utils.send_email(u, message)
        return render_to_response('pool/verify_user_success.html', context)
    except models.OrganizationUser.DoesNotExist:

        context['error'] = "Whoops, we can't find a user that matches this key.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help."
        return render_to_response('pool/verify_user_fail.html', context)


def create_user(request):
    context = {}
    context['host_name'] = settings.HOST_NAME
    context['user'] = None

    if request.method == "POST":

        # must have these params.
        REQUIRED_PARAMS = ['first_name', 'last_name', 'email_address', 'username', 'phone_number', 'preferred_contact', 'organization_id', 'password', 'shared_secret']
        for param in REQUIRED_PARAMS:
            if not request.POST.get(param, None):
                context['error'] = "Whoops, you're missing a parameter, <strong>%s</strong>, in your request.<br/>Email <a href='mailto:jeremy.bowers@nytimes.com'>the admin</a> for help." % param
                return render_to_response('pool/create_user_fail.html', context)

        # Make sure this is sent to people when they register.
        if request.POST['shared_secret'].strip() == settings.SHARED_SECRET:

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
            message = {}
            message['subject'] = "whitehousepool.org: Verify your email"
            message['body'] = "Someone registered an account with http://whitehousepool.org/ from this account\n"
            message['body'] += "If this was you, please click this link to verify your account.\n"
            message['body'] += "%s/pool/user/verify/%s/" % (settings.HOST_NAME, organization_user.temporary_code)

            if not request.POST.get('test', None):
                utils.send_email(organization_user, message)
                return render_to_response('pool/create_user_success.html', context)

            else:
                return HttpResponse(message['body'])

    if request.method == "GET":
        context.update(csrf(request))
        context['organizations'] = models.Organization.objects.all().values('organization_name', 'id').order_by('organization_name')
        return render_to_response('pool/create_user.html', context)

    return HttpResponse('400 error')

def calendar_entry(request, offer_code):
    try:
        offer = models.PoolSpotOffer.objects.get(offer_code=offer_code)

        if offer.pool_spot:
            c = Calendar()
            e = Event()
            e.name = "%s: trip to %s" % (offer.pool_spot.seat, offer.pool_spot.trip.location)
            e.description = "%s accepted by %s for the %s trip, %s through %s." % (
                    offer.pool_spot.seat,
                    offer.resolving_user,
                    offer.pool_spot.trip.location,
                    offer.pool_spot.trip.start_date,
                    offer.pool_spot.trip.end_date)
            e.begin = offer.date.isoformat()
            e.make_all_day()
            c.events.append(e)
            return HttpResponse(str(c), content_type="text/calendar")

            # For debuggging the ICS file.
            # return HttpResponse(str(c))

        else:
            return HttpResponse('400 error')
    except models.PoolSpotOffer.DoesNotExist:
        return HttpResponse('400 error')

def resolve_seat_offer(request, offer_action, offer_code):
    context = {}
    context['host_name'] = settings.HOST_NAME
    context['user'] = None

    # There must be a user ID associated with this request.
    # Guessing both a user ID and an offer code would be hard.
    # Vulnerable only to users who did receive the email
    # changing to a different user.
    if request.GET.get('ou', None):

        # Find the organization user matching this Id.
        try:
            context['user'] = models.OrganizationUser.objects.get(id=request.GET['ou'])

        except models.OrganizationUser.DoesNotExist:
            return HttpResponse('400 error')

    # Only do things if we find the user.
    if context['user']:
        try:

            # Find the offer.
            offer = models.PoolSpotOffer.objects.get(offer_code=offer_code)

            # If someone is accepting the offer and we can
            # find the offer, continue.
            if offer_action == "accept":
                if not offer.pool_spot:
                    offer.pool_spot.organization = offer.organization
                    offer.pool_spot.save()

                template_path = 'pool/offer_accept.html'

            elif offer_action == "decline":
                template_path = 'pool/offer_decline.html'

            else:
                return HttpResponse('400 error')

            # Resolve the offer.
            offer.resolving_user = context['user']

            if offer.active:
                offer.active = False
                offer.save()

            context['offer'] = offer
            return render_to_response(template_path, context)

        except models.PoolSpotOffer.DoesNotExist:
            return HttpResponse('400 error')

    else:
        # If there's no user, fail.
        return HttpResponse('400 error')

