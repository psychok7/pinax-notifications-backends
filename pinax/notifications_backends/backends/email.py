from django.conf import settings
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext
from django.template.loader import select_template

from core.utils import get_class_from_path

from pinax.notifications.backends.email import EmailBackend

from mail_templated import send_mail

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


class HtmlEmailBackend(EmailBackend):

    def deliver(self, recipient, sender, notice_type, extra_context):
        context = self.default_context()
        context.update({
            "recipient": recipient,
            "sender": sender,
            "notice": ugettext(notice_type.display),
        })
        context.update(extra_context)

        # Added support for Html Email templates using:
        # https://github.com/artemrizhov/django-mail-templated

        try:
            template = select_template(
                [
                    "pinax/notifications/{0}/{1}".format(
                        notice_type.label, "html.email"),
                    "pinax/notifications/{0}".format(
                        notice_type.label, "html.email")
                ]
            )

        except TemplateDoesNotExist:
            # We just ignore the backend if the template does not exist.
            pass
        else:
            send_mail(
                template_name=template.template.name, context=context,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email]
            )

    def deliver_bulk(self, recipients, sender, notice_type, extra_context):
        raise NotImplementedError()
