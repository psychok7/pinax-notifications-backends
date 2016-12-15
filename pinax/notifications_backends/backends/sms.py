from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext
from .base import BaseBackend
from core.utils import get_class_from_path

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
        if can_send:
            return True
        return False

    def deliver(self, recipient, sender, notice_type, extra_context):
        raise NotImplementedError()

    def deliver_bulk(self, recipients, sender, notice_type, extra_context):
        """
        Sending SMS using:
        https://github.com/stefanfoulis/django-sendsms/
        """
        print("Sending Bulk Sms... ")
        context = self.default_context()
        context.update({
            "sender": sender,
            "notice": ugettext(notice_type.display),
            "current_site": context['current_site'].domain
        })
        context.update(extra_context)

        try:
            messages = self.get_formatted_messages(
                ("sms.txt",), notice_type.label, context)
        except TemplateDoesNotExist:
            # We just ignore the backend if the template does not exist.
            pass
        else:
            body = messages["sms.txt"].strip().encode('utf-8')

            mobile_phones = []
            for recipient in recipients:
                if context.get('mobile_phone') and len(recipients) == 1:
                    # In case we need to override the default user phone number
                    mobile_phones.append(context['mobile_phone'])
                else:
                    if mobile_phone_path:
                        mobile_phone = getattr(recipient, mobile_phone_path)
                    else:
                        userprofile = getattr(recipient, 'userprofile')
                        mobile_phone = getattr(userprofile, 'mobile_phone')

                    mobile_phones.append(mobile_phone)

            api.send_sms(body=body, from_phone=from_phone, to=mobile_phones)

            if use_notice_model:
                Notice = get_class_from_path(
                    path='pinax.notifications_backends.models.Notice')

                # Based on http://stackoverflow.com/a/7390947
                # This is mostly a log for sent notifications.
                for recipient in recipients:
                    Notice.objects.create(
                        recipient=recipient, message=body, notice_type=notice_type,
                        sender=sender, medium='sms'
                    )
