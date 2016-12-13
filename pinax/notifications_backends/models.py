from __future__ import unicode_literals
from __future__ import print_function

from collections import defaultdict

from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language, activate
from django.core.urlresolvers import reverse

from .managers import NoticeManager

from pinax.notifications.models import NoticeType, LanguageStoreNotAvailable, \
    get_notification_language, queue
from pinax.notifications.utils import load_media_defaults

NOTICE_MEDIA, NOTICE_MEDIA_DEFAULTS = load_media_defaults()


class Notice(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="received_notices",
        verbose_name=_("recipient"))
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name="sent_notices",
        verbose_name=_("sender"))
    message = models.TextField(_("message"))
    notice_type = models.ForeignKey(NoticeType, verbose_name=_("notice type"))
    medium = models.CharField(_("medium"), max_length=100, choices=NOTICE_MEDIA)
    added = models.DateTimeField(_("added"), db_index=True, default=timezone.now)
    unseen = models.BooleanField(_("unseen"), db_index=True, default=True)
    archived = models.BooleanField(_("archived"), default=False)
    on_site = models.BooleanField(_("on site"), default=False)

    objects = NoticeManager()

    def __unicode__(self):
        return self.message

    def archive(self):
        self.archived = True
        self.save()

    def is_unseen(self):
        """
        returns value of self.unseen but also changes it to false.
        Use this in a template to mark an unseen notice differently the first
        time it is shown.
        """
        unseen = self.unseen
        if unseen:
            self.unseen = False
            self.save()
        return unseen

    class Meta:
        verbose_name = _("notice")
        verbose_name_plural = _("notices")

    def get_absolute_url(self):
        return reverse("notification_notice", args=[str(self.pk)])


def send_now(users, label, extra_context=None, sender=None, scoping=None):
    """
    Creates a new notice. This differs from
    pinax.notifications.models import send because it allows us to send bulk
    notifications.

    This is intended to be how other apps create new notices.
    notification.send(users, "friends_invite_sent", {
        "spam": "eggs",
        "foo": "bar",
    )
    """
    sent = False
    if extra_context is None:
        extra_context = {}

    notice_type = NoticeType.objects.get(label=label)

    current_language = get_language()

    users_to_send = defaultdict(list)

    for user in users:
        # get user language for user from language store defined in
        # NOTIFICATION_LANGUAGE_MODULE setting
        try:
            language = get_notification_language(user)
        except LanguageStoreNotAvailable:
            language = None

        if language is not None:
            # activate the user's language
            activate(language)

        for backend in settings.PINAX_NOTIFICATIONS_BACKENDS.values():
            if backend.can_send(user, notice_type, scoping=scoping):
                backend_name = backend.__class__.__name__
                if backend_name != 'CustomEmailBackend' and \
                        backend_name != 'HtmlEmailBackend':
                    users_to_send[backend].append(user)
                else:
                    # If the backend is the default email backend we want to
                    # send the emails individually.
                    backend.deliver(user, sender, notice_type, extra_context)
                    sent = True

    for backend, users in users_to_send.iteritems():
        backend.deliver_bulk(users, sender, notice_type, extra_context)

    if users_to_send:
        sent = True

    # reset environment to original language
    activate(current_language)
    return sent


def send(*args, **kwargs):
    """
    A basic interface around both queue and send_now. This honors a global
    flag NOTIFICATION_QUEUE_ALL that helps determine whether all calls should
    be queued or not. A per call ``queue`` or ``now`` keyword argument can be
    used to always override the default global behavior.
    """
    queue_flag = kwargs.pop("queue", False)
    now_flag = kwargs.pop("now", False)
    assert not (queue_flag and now_flag), "'queue' and 'now' cannot both be True."
    if queue_flag:
        return queue(*args, **kwargs)
    elif now_flag:
        return send_now(*args, **kwargs)
    else:
        if settings.PINAX_NOTIFICATIONS_QUEUE_ALL:
            return queue(*args, **kwargs)
        else:
            return send_now(*args, **kwargs)
