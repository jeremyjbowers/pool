import os

import ftfy
import requests
from twilio.rest import TwilioRestClient

def increment_seat_order(idx, seat_pool):
    try:
        next_organization = seat_pool[idx+1]
    except IndexError:
        next_organization = seat_pool[0]
    return next_organization

def clean_unicode(possible_string):
    if isinstance(possible_string, basestring):
        string = possible_string
        string = string.strip()
        string = string.decode('utf-8')
        string = unicode(string)
        string = ftfy.fix_text(string)
        return string
    return possible_string

def format_phone_number(possible_phone_number):
    phone = clean_unicode(possible_phone_number)
    phone = phone.replace('-','').replace(' ', '').replace('(', '').replace(')', '').replace('.', '')
    try:
        int(phone)
        return (phone, False)
    except ValueError:
        return (possible_phone_number, True)

def send_text(obj, message):
    """
    obj = OrganizationUser instance.
    message = {
        "subject": "Here is the message subject.",
        "body": "Here is the message body."
    }
    """
    client = TwilioRestClient(
        os.environ.get('POOL_TWILIO_ACCOUNT_SID', None),
        os.environ.get('POOL_TWILIO_AUTH_TOKEN', None)
    )
    b = client.messages.create(
        body=message.get('body', None),
        to="+1%s" % obj.phone_number,
        from_=os.environ.get('POOL_TWILIO_PHONE_NUMBER', None),
    )

def send_email(obj, message):
    """
    obj = OrganizationUser instance.
    message = {
        "subject": "Here is the message subject.",
        "body": "Here is the message body."
    }
    """
    return requests.post(
        "https://api.mailgun.net/v3/mg.whitehousepool.org/messages",
        auth=("api", os.environ.get('POOL_MAILGUN_API_KEY', None)),
        data={"from": "Pooler (whitehousepool.org) <mailgun@mg.whitehousepool.org>",
            "to": [obj.user.email],
            "subject": message.get('subject', None),
            "text": message.get('body', None)
        }
    )