from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pinax.notifications.utils import get_class_from_path
from .base import BaseBackend
from sendsms import api


try:
    use_notice_model = getattr(settings, 'PINAX_USE_NOTICE_MODEL')
except AttributeError:
    use_notice_model = None

try:
    mobile_phone_path = getattr(settings, 'PINAX_SMS_MOBILE_PHONE_PATH')
except AttributeError:
    mobile_phone_path = None

try:
    from_phone = getattr(settings, 'PINAX_SMS_DEFAULT_FROM_PHONE')
except AttributeError:
    raise ImproperlyConfigured('Please add a default FROM mobile number')


class SmsBackend(BaseBackend):
    spam_sensitivity = 2

    def can_send(self, user, notice_type, scoping):
        can_send = super(SmsBackend, self).can_send(user, notice_type, scoping)

        if mobile_phone_path is not None:
            mobile_phone = getattr(user, mobile_phone_path)
        else:
            userprofile = getattr(user, 'userprofile')
            mobile_phone = getattr(userprofile, 'mobile_phone')

        if can_send and mobile_phone:
            return True
        return False

    def deliver(self, recipient, sender, notice_type, extra_context):
        context = self.default_context()
        context['current_site'] = context['current_site'].domain
        context.update(extra_context)

        if mobile_phone_path:
            mobile_phone = getattr(recipient, mobile_phone_path)
        else:
            userprofile = getattr(recipient, 'userprofile')
            mobile_phone = getattr(userprofile, 'mobile_phone').split(',')

        if context.get('body'):
            api.send_sms(
                body=context['body'], from_phone=from_phone, to=mobile_phone
            )

            if use_notice_model:
                Notice = get_class_from_path(
                    path='pinax.notifications.models.Notice')

                # Based on http://stackoverflow.com/a/7390947
                # This is mostly a log for sent notifications.
                Notice.objects.create(
                    recipient=recipient, message=context['body'],
                    notice_type=notice_type, sender=sender,
                    medium='sms'
                )
