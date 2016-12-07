from django.contrib import admin

from pinax.notifications_backends.models import Notice


class NoticeAdmin(admin.ModelAdmin):
    list_display = [
        "message", "recipient", "sender", "medium", "notice_type", "added",
        "unseen", "archived"]
    list_filter = ["medium", "notice_type", "added"]
    raw_id_fields = ["recipient", "sender"]

admin.site.register(Notice, NoticeAdmin)
