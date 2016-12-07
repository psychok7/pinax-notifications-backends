from django.conf import settings


from core.utils import get_class_from_path
from pinax.notifications.backends.email import EmailBackend


try:
    use_notice_model = getattr(settings, 'PINAX_USE_NOTICE_MODEL')
except AttributeError:
    use_notice_model = None


class CustomEmailBackend(EmailBackend):

    def deliver(self, recipient, sender, notice_type, extra_context):
        print("Sending Email... ")
        super(
            CustomEmailBackend, self
        ).deliver(recipient, sender, notice_type, extra_context)

        if use_notice_model:
            Notice = get_class_from_path(
                path='pinax.notifications_backends.models.Notice')

            # Based on http://stackoverflow.com/a/7390947
            # This is mostly a log for sent notifications.
            Notice.objects.create(
                recipient=recipient, message=notice_type.description,
                notice_type=notice_type,  sender=sender, medium='email'
            )

    def deliver_bulk(self, recipients, sender, notice_type, extra_context):
        raise NotImplementedError()
