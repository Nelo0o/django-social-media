from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse


@login_required
@require_POST
def follow_user(request, username):
    """Vue pour suivre un utilisateur"""
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    
    try:
        success = request.user.profile.follow(target_profile)
        
        return JsonResponse({
            'success': success,
            'is_following': request.user.profile.is_following(target_profile),
            'followers_count': target_profile.followers_count,
            'message': 'Utilisateur suivi avec succès' if success else 'Vous suivez déjà cet utilisateur'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def unfollow_user(request, username):
    """Vue pour ne plus suivre un utilisateur"""
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    
    success = request.user.profile.unfollow(target_profile)
    
    return JsonResponse({
        'success': success,
        'is_following': request.user.profile.is_following(target_profile),
        'followers_count': target_profile.followers_count,
        'message': 'Vous ne suivez plus cet utilisateur' if success else 'Vous ne suiviez pas cet utilisateur'
    })
