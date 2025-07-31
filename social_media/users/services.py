from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count
from .models import UserProfile
from tweets.models import Tweet


class UserService:
    @staticmethod
    def get_user_profile_data(username=None, current_user=None):
        if username:
            profile_user = get_object_or_404(User, username=username)
            profile = profile_user.profile
            is_own_profile = current_user and current_user.is_authenticated and profile_user == current_user
            
            is_following = False
            if current_user and current_user.is_authenticated and not is_own_profile:
                is_following = current_user.profile.is_following(profile)
        else:
            if not current_user or not current_user.is_authenticated:
                raise ValueError("Utilisateur non connecté")
            
            profile_user = current_user
            profile = current_user.profile
            is_own_profile = True
            is_following = False
        
        return {
            'profile_user': profile_user,
            'profile': profile,
            'is_own_profile': is_own_profile,
            'is_following': is_following,
        }
    
    @staticmethod
    def get_user_tweets_with_metadata(profile, current_user=None):
        return Tweet.objects.for_user_profile(profile, current_user)
    
    @staticmethod
    def search_users(query, current_user=None, limit=100):
        current_user_profile = None
        if current_user and current_user.is_authenticated:
            current_user_profile = current_user.profile
        
        return UserProfile.objects.for_search(query, current_user_profile, limit)
    
    @staticmethod
    def get_user_suggestions(current_user, limit=5):
        if not current_user or not current_user.is_authenticated:
            return UserProfile.objects.none()
        
        return UserProfile.objects.for_suggestions(current_user.profile, limit)
    
    @staticmethod
    def get_home_feed(current_user=None, limit=50):
        user_profile = None
        if current_user and current_user.is_authenticated:
            user_profile = current_user.profile
        
        return Tweet.objects.for_home_feed(user_profile).recent(limit)
    
    @staticmethod
    def get_user_statistics(profile):
        return {
            'tweets_count': profile.tweets_count,
            'comments_count': profile.comments_count,
            'liked_tweets_count': profile.liked_tweets_count,
            'followers_count': profile.followers_count,
            'following_count': profile.following_count,
        }
