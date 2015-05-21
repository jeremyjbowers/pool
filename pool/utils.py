def increment_seat_order(idx, seat_pool):
    try:
        next_organization = seat_pool[idx+1]
    except IndexError:
        next_organization = seat_pool[0]
    return next_organization

def format_phone_number(possible_phone_number):
    phone = possible_phone_number
    phone = phone.replace('-','').replace(' ', '').replace('(', '').replace(')', '').replace('.', '')
    try:
        int(phone)
        return (phone, False)
    except ValueError:
        return (possible_phone_number, True)

def send_text(obj, message):
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
    return requests.post(
        "https://api.mailgun.net/v3/mg.whitehousepool.org/messages",
        auth=("api", os.environ.get('POOL_MAILGUN_API_KEY', None)),
        data={"from": "PoolBot <mailgun@mg.whitehousepool.org>",
            "to": [obj.user.email],
            "subject": message.get('subject', None),
            "text": message.get('body', None)
        }
    )