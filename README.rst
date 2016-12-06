Pinax Notifications Backends
============================

`pinax-notifications-backends` is a Django application that implements a few backends for `pinax-notifications` (Using a more up to date pinax-notifications fork https://github.com/Ubiwhere/pinax-notifications/tree/notice_model).

Currently the backends that we support are for sending SMS's (https://github.com/stefanfoulis/django-sendsms) and Push Notifications (https://github.com/jleclanche/django-push-notifications)

The pinax-notifications fork that we are using stores notices in the database, using a `Notice` model, so that the user can see a list of notices (a.k.a logs). This model has been taken from the old `django-notification`.

Quick start
-----------

1. Add "pinax.notifications_backends" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pinax.notifications_backends',
    ]

2. Then, add the following item to `settings.PINAX_NOTIFICATIONS_BACKENDS`::

    PINAX_NOTIFICATIONS_BACKENDS = [
        ("email", "pinax.notifications.backends.email.EmailBackend"),
        ("sms", "pinax.notifications_backends.backends.sms.SmsBackend"),
        (
            "push_notifications",
            "pinax.notifications_backends.backends.push_notifications."
            "PushNotificationBackend"
        ),
    ]

3. Example on how to send a notification using push notifications::

    from pinax.notifications.models import send
    from django.contrib.auth import get_user_model
    users = get_user_model().objects.filter(email='test@example.com')
    extra_context = {"subject": "", "body": "", "aps": {"alert": {"body": "", "title": ""}}}
    send(users, "label", extra_context)

4. Example on how to send a SMS using "django-sendsms" http://www.bulksms.com/ (available only if this PR gets merged https://github.com/stefanfoulis/django-sendsms/pull/17)::

    settings.py:
        # Make sure you have "django-sendsms" properly configured
        SENDSMS_BACKEND = 'sendsms.backends.bulksms.SmsBackend'
        SENDSMS_BULKSMS_USERNAME = 'xxx'
        SENDSMS_BULKSMS_PASSWORD = 'yyy'
    
        PINAX_SMS_DEFAULT_FROM_PHONE = '+41791111111'
        # Optional
        PINAX_SMS_MOBILE_PHONE_PATH = 'userprofile.mobile_phone'
    
    from pinax.notifications.models import send
    from django.contrib.auth import get_user_model
    users = get_user_model().objects.filter(email='test@example.com')
    send(users, "label", extra_context={"body": "yyy"})




