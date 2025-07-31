from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .services import FollowService


@login_required
@require_POST
def follow_user(request, username):
    result = FollowService.follow_user(request.user, username)
    return JsonResponse(result, status=400 if not result['success'] else 200)


@login_required
@require_POST
def unfollow_user(request, username):
    result = FollowService.unfollow_user(request.user, username)
    return JsonResponse(result)
