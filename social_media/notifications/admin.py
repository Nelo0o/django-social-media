from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'seen', 'created_at')
    list_filter = ('notification_type', 'seen', 'created_at')
    search_fields = ('recipient__user__username', 'sender__user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipient__user', 'sender__user', 'tweet__author__user'
        )
