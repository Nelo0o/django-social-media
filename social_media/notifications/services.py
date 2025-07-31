from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Notification


class NotificationService:
    @staticmethod
    def get_user_notifications(user_profile, page=1, per_page=20):
        notifications = Notification.objects.filter(
            recipient=user_profile
        ).select_related('sender__user', 'tweet__author__user').order_by('-created_at')
        
        paginator = Paginator(notifications, per_page)
        page_obj = paginator.get_page(page)
        
        return {
            'notifications': page_obj,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        }
    
    @staticmethod
    def mark_all_as_seen(user_profile):
        return Notification.mark_all_as_seen(user_profile)
    
    @staticmethod
    def mark_notification_as_seen(user_profile, notification_id):
        try:
            notification = get_object_or_404(
                Notification, 
                id=notification_id, 
                recipient=user_profile
            )
            
            notification.mark_as_seen()
            
            return {
                'success': True,
                'message': 'Notification marquée comme vue'
            }
            
        except Exception:
            return {
                'success': False,
                'error': 'Notification non trouvée ou erreur'
            }
    
    @staticmethod
    def get_unread_count(user_profile):
        return Notification.get_unread_count(user_profile)
    
    @staticmethod
    def create_notification(notification_type, sender_profile, recipient_profile, tweet=None):
        if sender_profile == recipient_profile:
            return None
        
        try:
            notification = Notification.objects.create(
                notification_type=notification_type,
                sender=sender_profile,
                recipient=recipient_profile,
                tweet=tweet
            )
            return notification
            
        except Exception:
            return None
    
    @staticmethod
    def delete_notification(notification_type, sender_profile, recipient_profile, tweet=None):
        filter_kwargs = {
            'notification_type': notification_type,
            'sender': sender_profile,
            'recipient': recipient_profile
        }
        
        if tweet:
            filter_kwargs['tweet'] = tweet
        
        deleted_count, _ = Notification.objects.filter(**filter_kwargs).delete()
        return deleted_count
