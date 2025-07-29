from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # utiliser les property
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def follow_manager(self):
        """Retourne le gestionnaire de follow pour ce profil"""
        return FollowManager(self)
    
    @property
    def followers_count(self):
        """Nombre d'abonnés (non bloqués)"""
        return self.follow_manager.followers_count
    
    @property
    def following_count(self):
        """Nombre d'abonnements (non bloqués)"""
        return self.follow_manager.following_count
    
    @property
    def followers(self):
        """QuerySet des profils qui suivent cet utilisateur"""
        return self.follow_manager.followers
    
    @property
    def following(self):
        """QuerySet des profils que cet utilisateur suit"""
        return self.follow_manager.following
    
    def follow(self, user_profile):
        """Suivre un utilisateur"""
        return self.follow_manager.follow(user_profile)
    
    def unfollow(self, user_profile):
        """Ne plus suivre un utilisateur"""
        return self.follow_manager.unfollow(user_profile)
    
    def is_following(self, user_profile):
        """Vérifier si on suit cet utilisateur"""
        return self.follow_manager.is_following(user_profile)
    
    @property
    def tweets_count(self):
        return self.tweets.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    @property
    def liked_tweets_count(self):
        return self.likes.count()


class FollowManager:
    """Gestionnaire pour les relations de suivi d'un UserProfile"""
    
    def __init__(self, user_profile):
        self.user_profile = user_profile
    
    @property
    def _follow_model(self):
        """Import lazy du modèle Follow pour éviter les imports circulaires"""
        from follows.models import Follow
        return Follow
    
    @property
    def followers_count(self):
        """Nombre d'abonnés (non bloqués)"""
        return self._follow_model.objects.filter(
            followed=self.user_profile,
            blocked=False
        ).count()
    
    @property
    def following_count(self):
        """Nombre d'abonnements (non bloqués)"""
        return self._follow_model.objects.filter(
            follower=self.user_profile,
            blocked=False
        ).count()
    
    @property
    def followers(self):
        """QuerySet des profils qui suivent cet utilisateur"""
        follower_ids = self._follow_model.objects.filter(
            followed=self.user_profile,
            blocked=False
        ).values_list('follower_id', flat=True)
        
        return UserProfile.objects.filter(id__in=follower_ids)
    
    @property
    def following(self):
        """QuerySet des profils que cet utilisateur suit"""
        following_ids = self._follow_model.objects.filter(
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
        
        follow_relation, created = self._follow_model.objects.get_or_create(
            follower=self.user_profile,
            followed=user_profile,
            defaults={'blocked': False}
        )
        
        if not created and follow_relation.blocked:
            follow_relation.blocked = False
            follow_relation.save()
        
        return True
    
    def unfollow(self, user_profile):
        """Ne plus suivre un utilisateur"""
        deleted_count, _ = self._follow_model.objects.filter(
            follower=self.user_profile,
            followed=user_profile
        ).delete()
        
        return deleted_count > 0
    
    def is_following(self, user_profile):
        """Vérifier si on suit cet utilisateur"""
        return self._follow_model.objects.filter(
            follower=self.user_profile,
            followed=user_profile,
            blocked=False
        ).exists()
    
    def block_follower(self, user_profile):
        """Bloquer un abonné"""
        try:
            follow_relation = self._follow_model.objects.get(
                follower=user_profile,
                followed=self.user_profile
            )
            follow_relation.blocked = True
            follow_relation.save()
            return True
        except self._follow_model.DoesNotExist:
            return False
    
    def unblock_follower(self, user_profile):
        """Débloquer un abonné"""
        try:
            follow_relation = self._follow_model.objects.get(
                follower=user_profile,
                followed=self.user_profile
            )
            follow_relation.blocked = False
            follow_relation.save()
            return True
        except self._follow_model.DoesNotExist:
            return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)