from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class FollowService:
    @staticmethod
    def follow_user(current_user, target_username):
        try:
            target_user = get_object_or_404(User, username=target_username)
            target_profile = target_user.profile
            
            if current_user == target_user:
                return {
                    'success': False,
                    'error': 'Vous ne pouvez pas vous suivre vous-même',
                    'is_following': False,
                    'followers_count': target_profile.followers_count
                }
            
            success = current_user.profile.follow(target_profile)
            message = 'Utilisateur suivi avec succès' if success else 'Vous suivez déjà cet utilisateur'
            
            return {
                'success': success,
                'is_following': current_user.profile.is_following(target_profile),
                'followers_count': target_profile.followers_count,
                'message': message
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'is_following': False,
                'followers_count': 0
            }
        except Exception:
            return {
                'success': False,
                'error': 'Une erreur est survenue',
                'is_following': False,
                'followers_count': 0
            }
    
    @staticmethod
    def unfollow_user(current_user, target_username):
        try:
            target_user = get_object_or_404(User, username=target_username)
            target_profile = target_user.profile
            
            success = current_user.profile.unfollow(target_profile)
            message = 'Vous ne suivez plus cet utilisateur' if success else 'Vous ne suiviez pas cet utilisateur'
            
            return {
                'success': success,
                'is_following': current_user.profile.is_following(target_profile),
                'followers_count': target_profile.followers_count,
                'message': message
            }
            
        except Exception:
            return {
                'success': False,
                'error': 'Une erreur est survenue',
                'is_following': True,
                'followers_count': 0
            }
    
    @staticmethod
    def get_follow_status(current_user, target_username):
        try:
            target_user = get_object_or_404(User, username=target_username)
            target_profile = target_user.profile
            
            return {
                'is_following': current_user.profile.is_following(target_profile),
                'followers_count': target_profile.followers_count,
                'following_count': target_profile.following_count,
                'can_follow': current_user != target_user
            }
            
        except Exception:
            return {
                'is_following': False,
                'followers_count': 0,
                'following_count': 0,
                'can_follow': False
            }
