from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    """Affiche la liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(
        recipient=request.user.profile
    ).select_related('sender__user', 'tweet__author__user')
    
    # Marquer automatiquement toutes les notifications comme vues
    Notification.mark_all_as_seen(request.user.profile)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': 0
    }
    
    return render(request, 'notifications/list.html', context)


@login_required
@require_POST
def mark_notification_as_seen(request, notification_id):
    """Marque une notification spécifique comme vue"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user.profile
    )
    
    notification.mark_as_seen()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification marquée comme vue'
    })


@login_required
@require_POST
def mark_all_notifications_as_seen(request):
    """Marque toutes les notifications comme vues"""
    Notification.mark_all_as_seen(request.user.profile)
    
    return JsonResponse({
        'success': True,
        'message': 'Toutes les notifications ont été marquées comme vues'
    })


@login_required
def get_unread_count(request):
    """Retourne le nombre de notifications non lues (API)"""
    count = Notification.get_unread_count(request.user.profile)
    
    return JsonResponse({
        'unread_count': count
    })
