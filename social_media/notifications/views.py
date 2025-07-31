from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification
from .services import NotificationService


@login_required
def notification_list(request):
    page_number = request.GET.get('page', 1)
    
    notification_data = NotificationService.get_user_notifications(
        user_profile=request.user.profile,
        page=page_number,
        per_page=20
    )
    
    NotificationService.mark_all_as_seen(request.user.profile)
    
    context = {
        'notifications': notification_data['notifications'],
        'unread_count': 0
    }
    
    return render(request, 'notifications/list.html', context)


@login_required
@require_POST
def mark_notification_as_seen(request, notification_id):
    result = NotificationService.mark_notification_as_seen(
        user_profile=request.user.profile,
        notification_id=notification_id
    )
    
    return JsonResponse(result)


@login_required
@require_POST
def mark_all_notifications_as_seen(request):
    count = NotificationService.mark_all_as_seen(request.user.profile)
    
    return JsonResponse({
        'success': True,
        'message': f'{count} notifications ont été marquées comme vues'
    })


@login_required
def get_unread_count(request):
    count = NotificationService.get_unread_count(request.user.profile)
    
    return JsonResponse({
        'unread_count': count
    })
