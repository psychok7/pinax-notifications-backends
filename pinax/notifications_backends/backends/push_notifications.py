from django.conf import settings
from pinax.notifications.utils import get_class_from_path
from _ssl import SSLError

from .base import BaseBackend


class PushNotificationBackend(BaseBackend):
    spam_sensitivity = 2

    def can_send(self, user, notice_type, scoping):
        can_send = super(PushNotificationBackend, self).can_send(user, notice_type, scoping)
        if can_send and user.email:
            return True
        return False

    def deliver(self, recipient, sender, notice_type, extra_context):
        context = self.default_context()
        context['current_site'] = context['current_site'].domain
        extra_context['aps'] = str(extra_context['aps']).encode("utf-8")
        context.update(extra_context)

        if context.get('subject') and context.get('body'):
            context['message'] = (
                context['subject'] + '\n\n' + context['body']
            )

        GCMDevice = get_class_from_path(
            path='push_notifications.models.GCMDevice')
        APNSDevice = get_class_from_path(
            path='push_notifications.models.APNSDevice')

        GCMError = get_class_from_path(path='push_notifications.gcm.GCMError')
        APNSError = get_class_from_path(path='push_notifications.apns.APNSError')

        gcm_device = GCMDevice.objects.filter(user=recipient)
        apns_device = APNSDevice.objects.filter(user=recipient)

        if gcm_device:
            try:
                gcm_device.first().send_message(None, extra=context)
            except GCMError as e:
                print('GCMError "%s"', str(e))

        if apns_device:
            try:
                apns_device.first().send_message(None, extra=context)
            except (APNSError, SSLError) as e:
                print('APNSError "%s"', str(e))

        if settings.PINAX_USE_NOTICE_MODEL:
            Notice = get_class_from_path(
                path='pinax.notifications.models.Notice')

            # Based on http://stackoverflow.com/a/7390947
            # This is mostly a log for sent notifications.
            if context.get('message'):
                Notice.objects.create(
                    recipient=recipient, message=context['message'],
                    notice_type=notice_type, sender=sender,
                    medium='push_notifications'
                )
