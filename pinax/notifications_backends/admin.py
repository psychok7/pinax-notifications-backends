from django.contrib import admin

from pinax.notifications_backends.models import Notice


class NoticeAdmin(admin.ModelAdmin):
    list_display = [
        "message", "recipient", "sender", "notice_type", "added", "unseen",
        "archived"]
    raw_id_fields = ["recipient", "sender"]

admin.site.register(Notice, NoticeAdmin)
