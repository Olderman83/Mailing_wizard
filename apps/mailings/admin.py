from django.contrib import admin
from .models import Mailing, MailingAttempt


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'status', 'start_datetime', 'end_datetime', 'recipients_count']
    list_filter = ['status', 'start_datetime']
    search_fields = ['message__subject']
    filter_horizontal = ['recipients']

    def recipients_count(self, obj):
        return obj.recipients.count()

    recipients_count.short_description = 'Количество получателей'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'mailing', 'status', 'attempt_datetime', 'recipient_email']
    list_filter = ['status', 'attempt_datetime']
    search_fields = ['mailing__message__subject', 'recipient_email']
