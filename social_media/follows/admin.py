from django.contrib import admin
from .models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'blocked', 'created_at')
    list_filter = ('blocked', 'created_at')
    search_fields = ('follower__user__username', 'followed__user__username')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'follower__user', 'followed__user'
        )
