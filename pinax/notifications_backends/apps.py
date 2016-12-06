from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class NotificationsBackendsConfig(AppConfig):
    name = 'pinax.notifications_backends'

    def ready(self):
        if 'pinax.notifications' not in settings.INSTALLED_APPS:
            msg = 'You need to include pinax.notifications in INSTALLED_APPS'
            raise ImproperlyConfigured(msg)
