from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('mark-seen/<int:notification_id>/', views.mark_notification_as_seen, name='mark_seen'),
    path('mark-all-seen/', views.mark_all_notifications_as_seen, name='mark_all_seen'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
]
