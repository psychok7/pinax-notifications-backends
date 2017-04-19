Pinax Notifications Backends
============================

`pinax-notifications-backends` is a Django application that implements a few backends for `pinax-notifications` (https://github.com/pinax/pinax-notifications) and it is based on https://github.com/jantoniomartin/condottieri_notification.

The backends that we support currently are for sending SMS's (https://github.com/stefanfoulis/django-sendsms/), Push Notifications (https://github.com/jleclanche/django-push-notifications) and HTML emails (https://github.com/artemrizhov/django-mail-templated)

The app also stores notices in the database, using a `Notice` model, so that the user can see a list of notices (a.k.a logs). This model idea has been taken from the old `django-notification`.

Apart from that we also override the pinax-notifications `send()` function so now we are able to send notices in BULK if we desire.

We are using forked versions of the mentioned packages, since we had to make a few changes/improvements. Make sure you install these dependencies first.

Quick start
-----------

1. Install the forked dependencies::

    pip install git+https://github.com/Ubiwhere/pinax-notifications.git@88e209d7475761cc8ce0726f571d60a74c3970de
    pip install git+https://github.com/psychok7/pinax-notifications-backends.git@3f6871d24658c6a7ea7de47590d696bba8caaafb
    
    # Available backends:
    pip install git+https://github.com/psychok7/django-sendsms.git@2bf4c20a6de8130e6cbcd1f651f619b638a498c3
    pip install django-push-notifications
    pip install django-mail-templated

2. Add "pinax.notifications_backends" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pinax.notifications_backends',
    ]

3. Then, add the following item to `settings.PINAX_NOTIFICATIONS_BACKENDS`::

    PINAX_NOTIFICATIONS_BACKENDS = [
        ("email", "pinax.notifications_backends.backends.email.HtmlEmailBackend"),
        # ("email", "pinax.notifications_backends.backends.email.CustomEmailBackend"),
        ("sms", "pinax.notifications_backends.backends.sms.SmsBackend"),
        (
            "push_notifications",
            "pinax.notifications_backends.backends.push_notifications."
            "PushNotificationBackend"
        ),
    ]

4. Example on how to send a notification using push notifications::

    from pinax.notifications_backends.models import send
    from django.contrib.auth import get_user_model
    users = get_user_model().objects.filter(email='test@example.com')
    send(users, "label")

5. Example on how to send a SMS using "django-sendsms" http://www.bulksms.com/ (available only if this PR gets merged https://github.com/stefanfoulis/django-sendsms/pull/17)::

    settings.py:
        # Make sure you have "django-sendsms" properly configured
        SENDSMS_BACKEND = 'sendsms.backends.bulksms.SmsBackend'
        SENDSMS_BULKSMS_USERNAME = 'xxx'
        SENDSMS_BULKSMS_PASSWORD = 'yyy'
    
        PINAX_SMS_DEFAULT_FROM_PHONE = '+41791111111'
        # Optional
        PINAX_SMS_MOBILE_PHONE_PATH = 'userprofile.mobile_phone'
    
    from pinax.notifications_backends.models import send
    from django.contrib.auth import get_user_model
    users = get_user_model().objects.filter(email='test@example.com')
    send(users, "label")
    # In case we need to send to a different number (works only for 1 recipient) instead of "PINAX_SMS_MOBILE_PHONE_PATH" we can:
    extra_context = {'mobile_phone': '+41791111111'}
    send(users, "label", extra_context=extra_context)




