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


    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def follow_manager(self):
        """Retourne le gestionnaire de follow pour ce profil"""
        from follows.models import FollowManager
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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)