from .models import Notification


def notifications_context(request):
    """
    Context processor pour ajouter le nombre de notifications non lues
    dans tous les templates
    """
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        unread_count = Notification.get_unread_count(request.user.profile)
        return {
            'notifications_unread_count': unread_count
        }
    return {
        'notifications_unread_count': 0
    }
