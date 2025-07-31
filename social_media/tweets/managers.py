from django.db import models
from django.db.models import Count, Exists, OuterRef, Prefetch


class TweetQuerySet(models.QuerySet):
    """QuerySet personnalisé pour optimiser les requêtes de tweets"""
    
    def with_interactions(self):
        """
        Précharge toutes les relations nécessaires pour l'affichage des tweets
        """
        return self.select_related(
            'author__user',
            'retweet_of__author__user'
        ).prefetch_related(
            'likes',
            'comments',
            'retweets',
            'hashtags',
            'retweet_of__likes',
            'retweet_of__comments',
            'retweet_of__retweets'
        )
    
    def with_counts(self):
        """
        Ajoute les compteurs de likes, comments et retweets via annotations
        """
        return self.annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
            retweets_count=Count('retweets', distinct=True)
        )
    
    def with_user_interactions(self, user_profile):
        """
        Ajoute les informations d'interaction pour un utilisateur spécifique
        """
        if not user_profile:
            return self
        
        return self.annotate(
            user_has_liked=Exists(
                self.model.objects.filter(
                    id=OuterRef('id'),
                    likes__user=user_profile
                )
            ),
            user_has_retweeted=Exists(
                self.model.objects.filter(
                    id=OuterRef('id'),
                    retweets__author=user_profile
                )
            ),
            is_liked_by_user=Exists(
                self.model.objects.filter(
                    id=OuterRef('id'),
                    likes__user=user_profile
                )
            ),
            is_retweeted_by_user=Exists(
                self.model.objects.filter(
                    id=OuterRef('id'),
                    retweets__author=user_profile
                )
            )
        )
    
    def exclude_blocked_users(self, user_profile):
        """
        Exclut les tweets des utilisateurs bloqués
        """
        if not user_profile:
            return self
        
        from follows.models import Follow
        
        blocked_users = Follow.objects.filter(
            models.Q(follower=user_profile, blocked=True) |
            models.Q(followed=user_profile, blocked=True)
        ).values_list('followed_id', 'follower_id')
        
        excluded_ids = set()
        for followed_id, follower_id in blocked_users:
            excluded_ids.add(followed_id)
            excluded_ids.add(follower_id)
        
        if excluded_ids:
            return self.exclude(author_id__in=excluded_ids)
        
        return self
    
    def for_home_feed(self, user_profile=None):
        """
        QuerySet optimisé pour le fil d'actualité
        """
        queryset = self.with_interactions().with_counts()
        
        if user_profile:
            queryset = queryset.exclude_blocked_users(user_profile)
            queryset = queryset.with_user_interactions(user_profile)
        
        return queryset.order_by('-created_at')
    
    def for_user_profile(self, profile_user, current_user=None):
        """
        QuerySet optimisé pour les tweets d'un profil utilisateur
        """
        queryset = self.filter(author=profile_user).with_interactions().with_counts()
        
        if current_user:
            queryset = queryset.with_user_interactions(current_user.profile)
        
        return queryset.order_by('-created_at')
    
    def by_hashtag(self, hashtag_label, user_profile=None):
        """
        QuerySet optimisé pour les tweets d'un hashtag
        """
        queryset = self.filter(
            hashtags__label__iexact=hashtag_label
        ).with_interactions().with_counts()
        
        if user_profile:
            queryset = queryset.exclude_blocked_users(user_profile)
            queryset = queryset.with_user_interactions(user_profile)
        
        return queryset.order_by('-created_at')
    
    def recent(self, limit=50):
        """
        Limite le nombre de tweets récents
        """
        return self[:limit]


class TweetManager(models.Manager):
    """Manager personnalisé pour le modèle Tweet"""
    
    def get_queryset(self):
        return TweetQuerySet(self.model, using=self._db)
    
    def with_interactions(self):
        return self.get_queryset().with_interactions()
    
    def with_counts(self):
        return self.get_queryset().with_counts()
    
    def for_home_feed(self, user_profile=None):
        return self.get_queryset().for_home_feed(user_profile)
    
    def for_user_profile(self, profile_user, current_user=None):
        return self.get_queryset().for_user_profile(profile_user, current_user)
    
    def by_hashtag(self, hashtag_label, user_profile=None):
        return self.get_queryset().by_hashtag(hashtag_label, user_profile)
