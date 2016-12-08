from django.conf import settings

from _ssl import SSLError

from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext
from .base import BaseBackend
from core.utils import get_class_from_path


GCMDevice = get_class_from_path(
    path='push_notifications.models.GCMDevice')
APNSDevice = get_class_from_path(
    path='push_notifications.models.APNSDevice')

GCMError = get_class_from_path(
    path='push_notifications.gcm.GCMError')
APNSError = get_class_from_path(
    path='push_notifications.apns.APNSError')

try:
    use_notice_model = getattr(settings, 'PINAX_USE_NOTICE_MODEL')
except AttributeError:
    use_notice_model = None


class PushNotificationBackend(BaseBackend):
    spam_sensitivity = 2

    def can_send(self, user, notice_type, scoping):
        can_send = super(
            PushNotificationBackend, self).can_send(user, notice_type, scoping)

        gcm_device_exists = GCMDevice.objects.filter(user=user).exists()
        apns_device_exists = APNSDevice.objects.filter(user=user).exists()

        if can_send and (gcm_device_exists or apns_device_exists):
            return True
        return False

    def deliver(self, recipient, sender, notice_type, extra_context):
        raise NotImplementedError()

    def deliver_bulk(self, recipients, sender, notice_type, extra_context):
        print("Sending Bulk Push Notifications... ")
        context = self.default_context()
        context.update({
            "notice": ugettext(notice_type.display),
            "current_site": context['current_site'].domain
        })
        if extra_context.get('aps'):
            extra_context['aps'] = str(extra_context['aps']).encode("utf-8")

        context.update(extra_context)

        try:
            messages = self.get_formatted_messages(
                ("push_notifications.txt",), notice_type.label, context)
        except TemplateDoesNotExist:
            # We just ignore the backend if the template does not exist.
            pass
        else:
            context['subject'] = context['notice'][:70].strip()
            context['body'] = messages["push_notifications.txt"][:70].strip()

            gcm_devices = GCMDevice.objects.filter(user__in=recipients)
            apns_devices = APNSDevice.objects.filter(user__in=recipients)

            if gcm_devices:
                try:
                    gcm_devices.send_message(None, extra=context)
                except GCMError as e:
                    print('GCMError "%s"', str(e))

            if apns_devices:
                try:
                    apns_devices.send_message(None, extra=context)
                except (APNSError, SSLError) as e:
                    print('APNSError "%s"', str(e))

            if use_notice_model:
                Notice = get_class_from_path(
                    path='pinax.notifications_backends.models.Notice')

                # Based on http://stackoverflow.com/a/7390947
                # This is mostly a log for sent notifications.
                if context.get('subject') and context.get('body'):
                    context['message'] = (
                        context['subject'] + '\n\n' + context['body']
                    )
                    for recipient in recipients:
                        Notice.objects.create(
                            recipient=recipient, message=context['message'],
                            notice_type=notice_type, sender=sender,
                            medium='push_notifications'
                        )
