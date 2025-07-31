from django.db import models
from django.core.exceptions import ValidationError


class Follow(models.Model):
    follower = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='followers')
    blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'followed')
    
    def __str__(self):
        return f"{self.follower.user.username} follows {self.followed.user.username}"


class FollowManager:
    """Gestionnaire pour les relations de suivi d'un UserProfile"""
    
    def __init__(self, user_profile):
        self.user_profile = user_profile
    
    @property
    def followers_count(self):
        """Nombre d'abonnés (non bloqués)"""
        return Follow.objects.filter(
            followed=self.user_profile,
            blocked=False
        ).count()
    
    @property
    def following_count(self):
        """Nombre d'abonnements (non bloqués)"""
        return Follow.objects.filter(
            follower=self.user_profile,
            blocked=False
        ).count()
    
    @property
    def followers(self):
        """QuerySet des profils qui suivent cet utilisateur"""
        from users.models import UserProfile
        follower_ids = Follow.objects.filter(
            followed=self.user_profile,
            blocked=False
        ).values_list('follower_id', flat=True)
        
        return UserProfile.objects.filter(id__in=follower_ids)
    
    @property
    def following(self):
        """QuerySet des profils que cet utilisateur suit"""
        from users.models import UserProfile
        following_ids = Follow.objects.filter(
            follower=self.user_profile,
            blocked=False
        ).values_list('followed_id', flat=True)
        
        return UserProfile.objects.filter(id__in=following_ids)
    
    def follow(self, user_profile):
        """Suivre un utilisateur"""
        if self.user_profile == user_profile:
            raise ValidationError("Vous ne pouvez pas vous suivre vous-même")
        
        if self.is_following(user_profile):
            return False  # Prévenir l'auto-suivi 
        
        follow_relation, created = Follow.objects.get_or_create(
            follower=self.user_profile,
            followed=user_profile,
            defaults={'blocked': False}
        )
        
        # Si la relation existe et est bloquée, la débloquer
        if not created and follow_relation.blocked:
            follow_relation.blocked = False
            follow_relation.save()
        
        return True
    
    def unfollow(self, user_profile):
        """Ne plus suivre un utilisateur"""
        deleted_count, _ = Follow.objects.filter(
            follower=self.user_profile,
            followed=user_profile
        ).delete()
        
        return deleted_count > 0
    
    def is_following(self, user_profile):
        """Vérifier si on suit cet utilisateur"""
        return Follow.objects.filter(
            follower=self.user_profile,
            followed=user_profile,
            blocked=False
        ).exists()
    
    def block_follower(self, user_profile):
        """Bloquer un abonné"""
        try:
            follow_relation = Follow.objects.get(
                follower=user_profile,
                followed=self.user_profile
            )
            follow_relation.blocked = True
            follow_relation.save()
            return True
        except Follow.DoesNotExist:
            return False
    
    def unblock_follower(self, user_profile):
        """Débloquer un abonné"""
        try:
            follow_relation = Follow.objects.get(
                follower=user_profile,
                followed=self.user_profile
            )
            follow_relation.blocked = False
            follow_relation.save()
            return True
        except Follow.DoesNotExist:
            return False
    
    def is_follower_blocked(self, user_profile):
        """Vérifier si un follower est bloqué"""
        try:
            follow_relation = Follow.objects.get(
                follower=user_profile,
                followed=self.user_profile
            )
            return follow_relation.blocked
        except Follow.DoesNotExist:
            return False